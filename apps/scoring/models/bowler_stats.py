from django.db import models

from matches.models import Innings
from coredata.models import Player

class BowlerStats(models.Model):
    innings = models.ForeignKey(
        Innings,
        on_delete=models.CASCADE,
        related_name="bowler_stats"
    )

    player = models.ForeignKey(
        Player,
        on_delete=models.PROTECT
    )

    balls = models.PositiveIntegerField(default=0)
    runs_conceded = models.PositiveIntegerField(default=0)
    wickets = models.PositiveSmallIntegerField(default=0)

    wides = models.PositiveSmallIntegerField(default=0)
    no_balls = models.PositiveSmallIntegerField(default=0)

    class Meta:
        unique_together = ("innings", "player")
