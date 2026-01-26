from uuid import UUID
from django.db import transaction

from scoring.models.ball import Ball
from scoring.models.aggregates import InningsAggregate
from scoring.models.batter_stats import BatterStats
from scoring.models.bowler_stats import BowlerStats
from scoring.models.wicket import BallWicket
from matches.models import MatchType

@transaction.atomic
def apply_scoring_engine(ball_id: UUID) -> None:
    """
    Apply scoring impact of a single Ball.
    Deterministic, replayable, offline-safe.
    """

    ball = Ball.objects.select_related(
        "innings", "match"
    ).get(id=ball_id)

    aggregate = InningsAggregate.objects.select_for_update().get(
        innings=ball.innings
    )

    match_type = ball.match.match_type

    # -------------------------
    # TEAM SCORE
    # -------------------------

    aggregate.runs += ball.runs_off_bat + ball.extra_runs
    aggregate.extras += ball.extra_runs

    # -------------------------
    # WICKETS
    # -------------------------

    if hasattr(ball, "wicket"):
        aggregate.wickets += 1

    # -------------------------
    # BALL / OVER COUNTING
    # -------------------------

    if ball.is_legal_delivery:
        aggregate.legal_balls += 1

        if ball.ball_in_over == match_type.balls_per_over:
            aggregate.completed_overs += 1

    # -------------------------
    # BATTER STATS
    # -------------------------

    batter = ball.striker

    batter_stats, _ = BatterStats.objects.get_or_create(
        innings=ball.innings,
        player=batter,
        defaults={
            "runs": 0,
            "balls": 0,
            "fours": 0,
            "sixes": 0,
            "is_out": False,
        },
    )

    batter_stats.runs += ball.runs_off_bat

    if ball.is_legal_delivery:
        batter_stats.balls += 1

    if ball.runs_off_bat == 4:
        batter_stats.fours += 1
    elif ball.runs_off_bat == 6:
        batter_stats.sixes += 1

    batter_stats.save()

    # -------------------------
    # BOWLER STATS
    # -------------------------

    bowler = ball.bowler

    bowler_stats, _ = BowlerStats.objects.get_or_create(
        innings=ball.innings,
        player=bowler,
        defaults={
            "runs_conceded": 0,
            "balls": 0,
            "wickets": 0,
        },
    )

    bowler_stats.runs_conceded += ball.runs_off_bat + ball.extra_runs

    if ball.is_legal_delivery:
        bowler_stats.balls += 1

    if hasattr(ball, "wicket"):
        bowler_stats.wickets += 1

    bowler_stats.save()

    # -------------------------
    # STRIKE ROTATION (AUTHORITATIVE)
    # -------------------------

    # Physical runs for crossing:
    # Runs off bat + Byes + Leg Byes
    # PLUS: Wides/No Balls if they involve crossing (usually Wide/NB > 1 run implies runs were taken)
    # Simplification: Odd runs total implies crossing if we assume 1 run penalty.
    # Accurate Logic:
    
    physical_runs = (
        ball.runs_off_bat +
        ball.bye_runs +
        ball.leg_bye_runs
    )

    # Add runs run on wides/no-balls
    # If wide_runs > 1, the extra runs are physical runs (assuming 1 is penalty)
    if ball.wide_runs > 1:
        physical_runs += (ball.wide_runs - 1)
    
    # If no_ball_runs > 1, the extra runs are physical runs (assuming 1 is penalty)
    if ball.no_ball_runs > 1:
        physical_runs += (ball.no_ball_runs - 1)

    if physical_runs % 2 == 1:
        aggregate.current_striker, aggregate.current_non_striker = (
            aggregate.current_non_striker,
            aggregate.current_striker,
        )

    # Over-end rotation
    if (
        ball.is_legal_delivery and
        ball.ball_in_over == match_type.balls_per_over
    ):
        aggregate.current_striker, aggregate.current_non_striker = (
            aggregate.current_non_striker,
            aggregate.current_striker,
        )
        aggregate.current_bowler = None

    # Wicket handling
    if hasattr(ball, "wicket"):
        dismissed_id = ball.wicket.dismissed_player_id
        
        if aggregate.current_striker_id == dismissed_id:
            aggregate.current_striker = None
        elif aggregate.current_non_striker_id == dismissed_id:
            aggregate.current_non_striker = None
        else:
            # Fallback (Edge case: retired hurt / timed out replacement logic might vary)
            # Default to clearing striker if ambiguity
            pass

    # -------------------------
    # FINALIZE
    # -------------------------

    aggregate.last_ball = ball
    aggregate.save()
