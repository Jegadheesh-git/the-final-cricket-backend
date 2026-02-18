import uuid
from django.db import models
from coredata.models import Player
from scoring.models import Ball


class BallFielding(models.Model):
    """
    Optional fielding details linked to a ball.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    ball = models.OneToOneField(
        Ball,
        on_delete=models.CASCADE,
        related_name="fielding"
    )

    fielder1 = models.ForeignKey(
        Player,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="fielding_primary"
    )

    fielder2 = models.ForeignKey(
        Player,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="fielding_secondary"
    )

    action = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )

    fielding_position = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )

    runs_saved = models.PositiveIntegerField(null=True, blank=True)
    runs_misfielded = models.PositiveIntegerField(null=True, blank=True)
    overthrow_runs = models.PositiveIntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["action"]),
            models.Index(fields=["fielding_position"]),
        ]

    def __str__(self):
        return f"Fielding for Ball {self.ball_id}"
