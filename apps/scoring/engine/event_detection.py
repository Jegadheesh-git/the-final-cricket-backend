from scoring.models.aggregates import InningsAggregate
from scoring.models.wicket import BallWicket
from matches.models import MatchType

def detect_wicket(ball):
    return BallWicket.objects.filter(ball=ball).exists()

def detect_over_end(ball, match_type):
    return (
        ball.is_legal_delivery and
        ball.ball_in_over == match_type.balls_per_over
    )

def detect_innings_end(aggregate, match_type):
    # All out
    if aggregate.wickets >= 10:
        return True

    # Overs exhausted (if limited)
    max_overs = aggregate.max_overs or match_type.max_overs
    if max_overs is not None:
        if aggregate.completed_overs >= max_overs:
            return True

    # Target achieved (chasing)
    if aggregate.is_chasing and aggregate.target_runs is not None:
        if aggregate.runs > aggregate.target_runs:
            return True

    return False

def detect_target_state(aggregate):
    if not aggregate.is_chasing or aggregate.target_runs is None:
        return None

    if aggregate.runs > aggregate.target_runs:
        return "WON"

    if aggregate.runs == aggregate.target_runs:
        return "TIED"

    return "IN_PROGRESS"

def detect_follow_on_required(match_type, innings_number):
    return (
        match_type.is_test and
        innings_number == 2 and
        match_type.follow_on_allowed
    )
