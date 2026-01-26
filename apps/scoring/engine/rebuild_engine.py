from scoring.models.aggregates import InningsAggregate
from scoring.models.batter_stats import BatterStats
from scoring.models.bowler_stats import BowlerStats
from scoring.models.ball import Ball

from scoring.engine.scoring_engine import apply_scoring_engine

def rebuild_innings_state(innings):
    # Preserve derived context BEFORE delete
    context = {
        "target_runs": None,
        "revised_target_runs": None,
        "max_overs": None,
        "is_chasing": False,
    }

    old_agg = InningsAggregate.objects.filter(innings=innings).first()
    if old_agg:
        context["target_runs"] = old_agg.target_runs
        context["revised_target_runs"] = old_agg.revised_target_runs
        context["max_overs"] = old_agg.max_overs
        context["is_chasing"] = old_agg.is_chasing
        old_agg.delete()
    else:
        # Fallback cleanup just in case (though filter().first() handles safety)
        InningsAggregate.objects.filter(innings=innings).delete()
        BatterStats.objects.filter(innings=innings).delete()
        BowlerStats.objects.filter(innings=innings).delete()

    # Fresh aggregate
    aggregate = InningsAggregate.objects.create(
        innings=innings,
        runs=0,
        wickets=0,
        legal_balls=0,
        completed_overs=0,
        **context
    )

    balls = Ball.objects.filter(
        innings=innings
    ).order_by("ball_number")

    for ball in balls:
        apply_scoring_engine(ball.id)
