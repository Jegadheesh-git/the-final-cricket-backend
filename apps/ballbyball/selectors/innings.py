"""
SELECTOR: Innings State

RESPONSIBILITY:
- Fetch active innings with aggregate and stats

MUST NEVER DO:
- Compute derived values
"""
from scoring.models import InningsAggregate, BatterStats, BowlerStats
from ballbyball.selectors.players import get_selectable_players


def build_active_innings_read_model(*, innings):
    aggregate, _ = InningsAggregate.objects.get_or_create(innings=innings)

    return {
        "match_id": innings.match_id,
        "innings_id": innings.id,
        "aggregate": {
            "runs": aggregate.runs,
            "wickets": aggregate.wickets,
            "legal_balls": aggregate.legal_balls,
            "completed_overs": aggregate.completed_overs,
            "extras": aggregate.extras,
            "current_striker": aggregate.current_striker_id,
            "current_non_striker": aggregate.current_non_striker_id,
            "current_bowler": aggregate.current_bowler_id,
            "is_chasing": aggregate.is_chasing,
            "target_runs": aggregate.target_runs,
            "revised_target_runs": aggregate.revised_target_runs,
            "target_achieved": aggregate.target_achieved,
        },
        "batting_stats": list(
            BatterStats.objects.filter(innings=innings).values()
        ),
        "bowling_stats": list(
            BowlerStats.objects.filter(innings=innings).values()
        ),
        "players": get_selectable_players(
            match=innings.match,
            innings=innings
        ),
    }
