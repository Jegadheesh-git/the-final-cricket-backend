import uuid
from django.db import models
from coredata.models import Team
from matches.models import Match, Innings


class InningsPenalty(models.Model):
    class AwardedTo(models.TextChoices):
        BATTING = "BATTING", "Batting"
        BOWLING = "BOWLING", "Bowling"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    match = models.ForeignKey(
        Match,
        on_delete=models.CASCADE,
        related_name="penalties"
    )

    innings = models.ForeignKey(
        Innings,
        on_delete=models.CASCADE,
        related_name="penalties_happened"
    )

    awarded_to_innings = models.ForeignKey(
        Innings,
        on_delete=models.CASCADE,
        related_name="penalties_awarded"
    )

    awarded_team = models.ForeignKey(
        Team,
        on_delete=models.PROTECT,
        related_name="penalties_awarded"
    )

    awarded_to = models.CharField(
        max_length=10,
        choices=AwardedTo.choices
    )

    reason = models.CharField(
        max_length=100
    )

    reason_other = models.CharField(
        max_length=200,
        blank=True,
        default=""
    )

    runs = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Penalty {self.runs} to {self.awarded_team} ({self.reason})"
