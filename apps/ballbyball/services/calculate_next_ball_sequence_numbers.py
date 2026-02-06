"""
SERVICE: Calculate Next Ball Sequence Numbers

RESPONSIBILITY:
- Calculate next ball_number
- Calculate over_number and ball_in_over
- Respect match type rules (balls per over)

MUST DO:
- Be pure and deterministic

MUST NEVER DO:
- Write to database
- Update aggregates or stats
"""
def calculate_next_ball_sequence_numbers(*, aggregate, balls_per_over):
    """
    Calculates next ball_number, over_number, ball_in_over.
    """
    next_ball_number = aggregate.legal_balls + 1

    completed_overs = aggregate.legal_balls // balls_per_over
    ball_in_over = (aggregate.legal_balls % balls_per_over) + 1
    over_number = completed_overs + 1

    return next_ball_number, over_number, ball_in_over
