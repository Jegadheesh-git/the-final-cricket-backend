from scoring.engine.event_detection import (
    detect_wicket,
    detect_over_end,
    detect_innings_end,
    detect_target_state,
    detect_follow_on_required,
)
from scoring.models.aggregates import InningsAggregate

from scoring.models.batter_stats import BatterStats
from scoring.models.bowler_stats import BowlerStats

def serialize_batter_stats(stats):
    if not stats:
        return None
    return {
        "player_id": str(stats.player_id),
        "runs": stats.runs,
        "balls": stats.balls,
        "fours": stats.fours,
        "sixes": stats.sixes,
        "is_out": stats.is_out,
    }

def serialize_bowler_stats(stats):
    if not stats:
        return None
    return {
        "player_id": str(stats.player_id),
        "balls": stats.balls,
        "runs_conceded": stats.runs_conceded,
        "wickets": stats.wickets,
        "wides": stats.wides,
        "no_balls": stats.no_balls,
        "overs": f"{stats.balls // 6}.{stats.balls % 6}" # Derived helper
    }

def build_ball_outcome(ball):
    aggregate = InningsAggregate.objects.get(innings=ball.innings)
    match = ball.match
    match_type = match.match_type

    wicket = detect_wicket(ball)
    over_end = detect_over_end(ball, match_type)
    innings_end = detect_innings_end(aggregate, match_type)

    target_state = detect_target_state(aggregate)
    ask_super_over = (
        innings_end and
        target_state == "TIED" and
        match_type.super_over_allowed
    )

    ask_follow_on = (
        innings_end and
        detect_follow_on_required(match_type, ball.innings.innings_number)
    )

    # Fetch Stats Objects
    striker_id = aggregate.current_striker_id
    non_striker_id = aggregate.current_non_striker_id
    bowler_id = aggregate.current_bowler_id
    
    striker_stats = None
    if striker_id:
        striker_stats = BatterStats.objects.filter(
            innings=aggregate.innings, player_id=striker_id
        ).first()

    non_striker_stats = None
    if non_striker_id:
        non_striker_stats = BatterStats.objects.filter(
            innings=aggregate.innings, player_id=non_striker_id
        ).first()

    bowler_stats = None
    if bowler_id and not over_end:
        bowler_stats = BowlerStats.objects.filter(
            innings=aggregate.innings, player_id=bowler_id
        ).first()


    return {
        "ball_id": str(ball.id),

        "events": {
            "wicket": wicket,
            "over_end": over_end,
            "innings_end": innings_end,
            "match_end": False,  # Phase 6 decides
            "target_achieved": target_state == "WON",
            "ask_super_over": ask_super_over,
            "ask_follow_on": ask_follow_on,
        },

        "actions_required": {
            "select_batter": wicket,
            "select_bowler": over_end,
            "confirm_super_over": ask_super_over,
            "confirm_follow_on": ask_follow_on,
        },

        "next_state": {
            "striker": serialize_batter_stats(striker_stats),
            "non_striker": serialize_batter_stats(non_striker_stats),
            "bowler": serialize_bowler_stats(bowler_stats),
        },

        "aggregates": {
            "runs": aggregate.runs,
            "wickets": aggregate.wickets,
            "overs": f"{aggregate.completed_overs}.{aggregate.legal_balls % match_type.balls_per_over}",
            "target": aggregate.target_runs,
        }
    }
