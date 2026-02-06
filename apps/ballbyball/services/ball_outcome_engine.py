"""
SERVICE: Ball Outcome Engine (Pure)

RESPONSIBILITY:
- Determine over-end
- Compute strike rotation based on physical runs
- Apply wicket impact to next striker/non-striker
- Return next participants + required actions (no DB writes)
"""


def calculate_physical_runs(ball):
    """
    Physical runs are used to determine crossing/strike rotation.
    """
    runs = ball.runs_off_bat + ball.bye_runs + ball.leg_bye_runs

    if ball.wide_runs > 1:
        runs += (ball.wide_runs - 1)

    if ball.no_ball_runs > 1:
        runs += (ball.no_ball_runs - 1)

    return runs


def is_over_end(*, ball, balls_per_over):
    return (
        ball.is_legal_delivery and
        ball.ball_in_over == balls_per_over
    )


def rotate_for_runs(*, striker_id, non_striker_id, physical_runs):
    if physical_runs % 2 == 1:
        return non_striker_id, striker_id
    return striker_id, non_striker_id


def rotate_for_over_end(*, striker_id, non_striker_id):
    return non_striker_id, striker_id


def apply_wicket_clear(*, striker_id, non_striker_id, dismissed_player_id):
    if dismissed_player_id is None:
        return striker_id, non_striker_id

    if dismissed_player_id == striker_id:
        return None, non_striker_id

    if dismissed_player_id == non_striker_id:
        return striker_id, None

    return striker_id, non_striker_id


def derive_next_state(
    *,
    striker_id,
    non_striker_id,
    bowler_id,
    ball,
    balls_per_over,
    dismissed_player_id=None,
):
    physical_runs = calculate_physical_runs(ball)

    next_striker, next_non_striker = rotate_for_runs(
        striker_id=striker_id,
        non_striker_id=non_striker_id,
        physical_runs=physical_runs,
    )

    over_end = is_over_end(
        ball=ball,
        balls_per_over=balls_per_over,
    )

    if over_end:
        next_striker, next_non_striker = rotate_for_over_end(
            striker_id=next_striker,
            non_striker_id=next_non_striker,
        )
        next_bowler = None
    else:
        next_bowler = bowler_id

    next_striker, next_non_striker = apply_wicket_clear(
        striker_id=next_striker,
        non_striker_id=next_non_striker,
        dismissed_player_id=dismissed_player_id,
    )

    actions = {
        "new_batter_select": (
            next_striker is None or next_non_striker is None
        ),
        "new_bowler_select": next_bowler is None,
        "over_end": over_end,
    }

    return {
        "next_striker": next_striker,
        "next_non_striker": next_non_striker,
        "next_bowler": next_bowler,
        "physical_runs": physical_runs,
        "over_end": over_end,
        "actions": actions,
    }
