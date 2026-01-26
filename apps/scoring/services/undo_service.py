from django.db import transaction
from django.shortcuts import get_object_or_404

from scoring.models.ball import Ball
from matches.models import Innings
from scoring.services.rebuild_service import rebuild_innings

@transaction.atomic
def undo_last_ball(innings_id):
    innings = get_object_or_404(Innings, id=innings_id)

    last_ball = (
        Ball.objects
        .filter(innings=innings)
        .order_by("-ball_number")
        .first()
    )

    if not last_ball:
        raise ValueError("No balls to undo")

    last_ball.delete()

    rebuild_innings(innings)
