import uuid
from django.db import models
from django.conf import settings

from matches.models import Match, Innings
from coredata.models import Team, Player

class Ball(models.Model):
    """
    Core immutable record of a single delivery.
    This is the ONLY source of truth for scoring.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Audit
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="balls_recorded"
    )

    # Context
    match = models.ForeignKey(
        Match,
        on_delete=models.CASCADE,
        related_name="balls"
    )

    innings = models.ForeignKey(
        Innings,
        on_delete=models.CASCADE,
        related_name="balls"
    )

    # Ordering (AUTHORITATIVE)
    ball_number = models.PositiveIntegerField(
        help_text="Sequential delivery order within the innings"
    )

    # Cricket position (STRUCTURAL)
    over_number = models.PositiveIntegerField(
        help_text="1-based over number"
    )

    ball_in_over = models.PositiveIntegerField(
        help_text="1-based delivery count within the over"
    )

    is_legal_delivery = models.BooleanField(
        default=True,
        help_text="Counts towards legal ball count"
    )

    # Participants (snapshot)
    batting_team = models.ForeignKey(
        Team,
        on_delete=models.PROTECT,
        related_name="balls_batted"
    )

    bowling_team = models.ForeignKey(
        Team,
        on_delete=models.PROTECT,
        related_name="balls_bowled"
    )

    striker = models.ForeignKey(
        Player,
        on_delete=models.PROTECT,
        related_name="balls_faced"
    )

    non_striker = models.ForeignKey(
        Player,
        on_delete=models.PROTECT,
        related_name="balls_non_striker"
    )

    bowler = models.ForeignKey(
        Player,
        on_delete=models.PROTECT,
        related_name="balls_bowled"
    )

    # Scoring facts (NON-DERIVABLE)
    runs_off_bat = models.PositiveSmallIntegerField(default=0)
    completed_runs = models.PositiveSmallIntegerField(
        default=0,
        help_text="Number of runs physically completed by running"
    )

    extra_runs = models.PositiveSmallIntegerField(default=0)

    # Extras breakdown (facts)
    bye_runs = models.PositiveSmallIntegerField(default=0)
    leg_bye_runs = models.PositiveSmallIntegerField(default=0)
    wide_runs = models.PositiveSmallIntegerField(default=0)
    no_ball_runs = models.PositiveSmallIntegerField(default=0)
    penalty_runs = models.PositiveSmallIntegerField(default=0)
    overthrow_runs = models.PositiveSmallIntegerField(default=0)

    # Wicket linkage handled via BallWicket model

    # Flags (SEMANTIC ONLY)
    is_boundary = models.BooleanField(default=False)
    is_short_run = models.BooleanField(default=False)

    no_ball_type = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        help_text="overstep / height / free-hit etc."
    )

    edit_later = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["innings", "ball_number"]
        unique_together = (
            ("innings", "ball_number"),
        )
        indexes = [
            models.Index(fields=["match", "innings"]),
            models.Index(fields=["innings", "ball_number"]),
            models.Index(fields=["bowler"]),
            models.Index(fields=["striker"]),
        ]

    def __str__(self):
        return f"Innings {self.innings_id} Ball #{self.ball_number}"
