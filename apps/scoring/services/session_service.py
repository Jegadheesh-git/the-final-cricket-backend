from uuid import UUID
from django.shortcuts import get_object_or_404

from matches.models import Match, Innings, PlayingXI
from scoring.models.aggregates import InningsAggregate
from coredata.models import Player

def start_scoring_session(match_id: UUID) -> dict:
    match = get_object_or_404(Match, id=match_id)

    if match.state not in ("READY", "IN_PROGRESS"):
        raise ValueError("Match is not in a scorable state")

    match_type = match.match_type

    # Latest innings (if any) - Using .last() to avoid field error on 'number'
    latest_innings = Innings.objects.filter(match=match).last()

    session_type = "FRESH"
    innings = None
    aggregate = None

    if latest_innings and latest_innings.state == "OPEN":
        session_type = "RESUME"
        innings = latest_innings
        aggregate = InningsAggregate.objects.filter(
            innings=innings
        ).first()

    # Decide teams for setup
    if innings:
        batting_team = innings.batting_team
        bowling_team = innings.bowling_team
    else:
        batting_team = match.team_a
        bowling_team = match.team_b

    # Playing XI (authoritative source)
    batting_players = Player.objects.filter(
        id__in=PlayingXI.objects.filter(
            match=match,
            team=batting_team
        ).values_list("player_id", flat=True)
    )

    bowling_players = Player.objects.filter(
        id__in=PlayingXI.objects.filter(
            match=match,
            team=bowling_team
        ).values_list("player_id", flat=True)
    )

    # Exclude dismissed batters if resuming
    dismissed_batter_ids = []
    if aggregate:
        dismissed_batter_ids = aggregate.batter_stats.filter(
            is_out=True
        ).values_list("player_id", flat=True)

    available_batters = batting_players.exclude(
        id__in=dismissed_batter_ids
    )

    available_bowlers = bowling_players

    return {
        "session_type": session_type,

        "match": {
            "id": match.id,
            "state": match.state,
            "match_mode": match.match_mode,
        },

        "match_type": {
            "innings_per_team": (match_type.max_innings // 2) if match_type.max_innings else 1,
            "max_overs_per_innings": match_type.max_overs,
            "max_balls_per_innings": (match_type.max_overs * match_type.balls_per_over) if match_type.max_overs else None,
            "balls_per_over": match_type.balls_per_over,
            "follow_on_allowed": match_type.follow_on_allowed,
        },

        "innings": (
            {
                "id": innings.id,
                "number": innings.innings_number,
                "batting_team": innings.batting_team_id,
                "bowling_team": innings.bowling_team_id,
            }
            if innings else None
        ),

        "current_state": (
            {
                "striker": aggregate.current_striker_id,
                "non_striker": aggregate.current_non_striker_id,
                "bowler": aggregate.current_bowler_id,
                "legal_balls_in_current_over":
                    aggregate.balls % match_type.balls_per_over,
            }
            if aggregate else None
        ),

        "available_players": {
            "batters": [
                {"id": p.id, "full_name": f"{p.first_name} {p.last_name}"} for p in available_batters
            ],
            "bowlers": [
                {"id": p.id, "full_name": f"{p.first_name} {p.last_name}"} for p in available_bowlers
            ],
        }
    }
