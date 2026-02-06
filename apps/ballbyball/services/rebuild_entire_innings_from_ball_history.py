"""
SERVICE: Rebuild Entire Innings from Ball History

RESPONSIBILITY:
- Recompute aggregate and stats from scratch
- Process balls sequentially

MUST DO:
- Be idempotent
- Be safe for audits and undo

MUST NEVER DO:
- Assume partial state
- Patch existing aggregates
"""
from scoring.models import (
    Ball,
    InningsAggregate,
    BatterStats,
    BowlerStats,
)
from ballbyball.services.ball_outcome_engine import (
    derive_next_state,
)
from ballbyball.services.innings_outcome_engine import (
    detect_target_state,
)

def rebuild_entire_innings_from_ball_history(*, innings):
    Ball.objects.filter(innings=innings).order_by("ball_number")

    InningsAggregate.objects.filter(innings=innings).update(
        runs=0,
        wickets=0,
        legal_balls=0,
        completed_overs=0,
        extras=0,
        current_striker=None,
        current_non_striker=None,
        current_bowler=None,
        last_ball=None,
    )

    BatterStats.objects.filter(innings=innings).update(
        runs=0,
        balls=0,
        fours=0,
        sixes=0,
        is_out=False,
        dismissal_ball=None,
    )
    BowlerStats.objects.filter(innings=innings).update(
        runs_conceded=0,
        balls=0,
        wickets=0,
        wides=0,
        no_balls=0,
    )

    for ball in Ball.objects.filter(innings=innings).order_by("ball_number"):
        wicket = getattr(ball, "wicket", None)
        dismissed_player_id = None
        wicket_type = None
        if wicket:
            dismissed_player_id = wicket.dismissed_player_id
            wicket_type = wicket.wicket_type

        outcome = derive_next_state(
            striker_id=ball.striker_id,
            non_striker_id=ball.non_striker_id,
            bowler_id=ball.bowler_id,
            ball=ball,
            balls_per_over=innings.match.match_type.balls_per_over,
            dismissed_player_id=dismissed_player_id,
        )

        aggregate = InningsAggregate.objects.get(innings=innings)
        aggregate.runs += ball.runs_off_bat + ball.extra_runs
        aggregate.extras += ball.extra_runs
        if wicket_type and dismissed_player_id:
            aggregate.wickets += 1
        if ball.is_legal_delivery:
            aggregate.legal_balls += 1
            if ball.ball_in_over == innings.match.match_type.balls_per_over:
                aggregate.completed_overs += 1
        aggregate.current_striker_id = outcome["next_striker"]
        aggregate.current_non_striker_id = outcome["next_non_striker"]
        aggregate.current_bowler_id = outcome["next_bowler"]
        aggregate.last_ball = ball
        aggregate.save()

        batter, _ = BatterStats.objects.get_or_create(
            innings=innings,
            player_id=ball.striker_id,
        )
        batter.runs += ball.runs_off_bat
        if ball.is_legal_delivery:
            batter.balls += 1
        if ball.runs_off_bat == 4:
            batter.fours += 1
        elif ball.runs_off_bat == 6:
            batter.sixes += 1
        if wicket_type and dismissed_player_id == ball.striker_id:
            batter.is_out = True
            batter.dismissal_ball = ball
        batter.save()

        bowler_stats, _ = BowlerStats.objects.get_or_create(
            innings=innings,
            player_id=ball.bowler_id,
        )
        bowler_stats.runs_conceded += (
            ball.runs_off_bat + ball.wide_runs + ball.no_ball_runs
        )
        if ball.wide_runs:
            bowler_stats.wides += 1
        if ball.no_ball_runs:
            bowler_stats.no_balls += 1
        if ball.is_legal_delivery:
            bowler_stats.balls += 1
        if wicket_type in {"BOWLED", "LBW", "CAUGHT", "STUMPED", "HIT_WICKET"}:
            credited_to_bowler = (
                wicket.dismissed_by_id is None or
                wicket.dismissed_by_id == ball.bowler_id
            ) if wicket else True
            if credited_to_bowler:
                bowler_stats.wickets += 1
        bowler_stats.save()

        target_state = detect_target_state(aggregate=aggregate)
        aggregate.target_achieved = target_state == "WON"
        aggregate.save(update_fields=["target_achieved"])
