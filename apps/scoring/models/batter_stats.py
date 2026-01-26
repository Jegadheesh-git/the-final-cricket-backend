from django.db import models
from .ball import Ball
from matches.models import Innings
from coredata.models import Player

class BatterStats(models.Model):
    innings = models.ForeignKey(
        Innings,
        on_delete=models.CASCADE,
        related_name="batter_stats"
    )

    player = models.ForeignKey(
        Player,
        on_delete=models.PROTECT
    )

    runs = models.PositiveIntegerField(default=0)
    balls = models.PositiveIntegerField(default=0)
    fours = models.PositiveSmallIntegerField(default=0)
    sixes = models.PositiveSmallIntegerField(default=0)

    is_out = models.BooleanField(default=False)
    dismissal_ball = models.ForeignKey(
        Ball,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    class Meta:
        unique_together = ("innings", "player")
