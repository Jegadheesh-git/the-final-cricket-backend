"""
SERVICE: Undo Last Recorded Ball

RESPONSIBILITY:
- Delete the most recent ball
- Delete all linked records
- Trigger full rebuild

MUST DO:
- Undo exactly ONE ball

MUST NEVER DO:
- Undo multiple balls
- Reverse calculations
"""
from django.db import transaction
from scoring.models import Ball
from .rebuild_entire_innings_from_ball_history import (
    rebuild_entire_innings_from_ball_history,
)


@transaction.atomic
def undo_last_recorded_ball(*, innings):
    last_ball = (
        Ball.objects.filter(innings=innings)
        .order_by("-ball_number")
        .first()
    )
    if not last_ball:
        return None

    last_ball.delete()
    rebuild_entire_innings_from_ball_history(innings=innings)
    return last_ball
