import uuid
from django.db import models
from coredata.models import Team
from scoring.models import Ball


class BallDRS(models.Model):
    """
    Optional DRS metadata for a ball.
    """

    class Decision(models.TextChoices):
        WICKET = "WICKET", "Wicket"
        NOT_OUT = "NOT_OUT", "Not Out"
        WIDE = "WIDE", "Wide"
        NO_BALL = "NO_BALL", "No Ball"
        LEGAL = "LEGAL", "Legal Ball"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    ball = models.OneToOneField(
        Ball,
        on_delete=models.CASCADE,
        related_name="drs"
    )

    is_appealed = models.BooleanField(default=False)
    review_team = models.ForeignKey(
        Team,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="drs_reviews"
    )
    review_team_side = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        help_text="BAT or BOWL"
    )

    on_field_decision = models.CharField(
        max_length=20,
        choices=Decision.choices,
        null=True,
        blank=True
    )

    overruled = models.BooleanField(default=False)

    final_decision = models.CharField(
        max_length=20,
        choices=Decision.choices,
        null=True,
        blank=True
    )

    decision_given_by_umpire = models.ForeignKey(
        "coredata.Umpire",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="drs_decisions_given"
    )

    third_umpire = models.ForeignKey(
        "coredata.Umpire",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="drs_third_umpire"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"DRS for Ball {self.ball_id}"
