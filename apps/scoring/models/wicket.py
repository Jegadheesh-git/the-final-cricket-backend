import uuid
from django.db import models
from coredata.models import Player, Team
from scoring.models import Ball

class BallWicket(models.Model):
    """
    Represents a wicket that occurred on a particular ball.
    Exists only if a dismissal happened.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    ball = models.OneToOneField(
        Ball,
        on_delete=models.CASCADE,
        related_name="wicket"
    )

    # Primary dismissal info
    wicket_type = models.CharField(
        max_length=30,
        choices=(
            ("BOWLED", "Bowled"),
            ("LBW", "LBW"),
            ("CAUGHT", "Caught"),
            ("RUN_OUT", "Run Out"),
            ("STUMPED", "Stumped"),
            ("HIT_WICKET", "Hit Wicket"),
            ("RETIRED_HURT", "Retired Hurt"),
            ("OBSTRUCTING_FIELD", "Obstructing the Field"),
            ("HANDLED_BALL", "Handled the Ball"),
            ("TIMED_OUT", "Timed Out"),
        )
    )

    dismissed_player = models.ForeignKey(
        Player,
        on_delete=models.PROTECT,
        related_name="dismissals"
    )

    # Bowler credited for wicket (NULL for run-out, retired hurt, etc.)
    dismissed_by = models.ForeignKey(
        Player,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="wickets_credited"
    )

    # Fielding involvement (all optional & conditional)
    caught_by = models.ForeignKey(
        Player,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="catches_taken"
    )

    stumped_by = models.ForeignKey(
        Player,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="stumpings_made"
    )

    run_out_fielder_1 = models.ForeignKey(
        Player,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="run_outs_primary"
    )

    run_out_fielder_2 = models.ForeignKey(
        Player,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="run_outs_secondary"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["wicket_type"]),
            models.Index(fields=["dismissed_player"]),
        ]

    def __str__(self):
        return f"{self.wicket_type} - {self.dismissed_player}"
