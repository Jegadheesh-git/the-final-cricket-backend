from django.db import models
from .ball import Ball
from matches.models import Innings
from coredata.models import Player

class InningsAggregate(models.Model):
    """
    Derived, rebuildable aggregate for an innings.
    NEVER the source of truth.
    """

    innings = models.OneToOneField(
        Innings,
        on_delete=models.CASCADE,
        related_name="aggregate"
    )

    # Core totals (derived)
    runs = models.PositiveIntegerField(default=0)
    wickets = models.PositiveSmallIntegerField(default=0)

    # Ball / over tracking (CRITICAL)
    legal_balls = models.PositiveIntegerField(default=0)
    completed_overs = models.PositiveIntegerField(default=0)

    # Extras
    extras = models.PositiveIntegerField(default=0)
    extra_penalty_runs = models.PositiveIntegerField(default=0)

    # Chase & target (nullable by design)
    is_chasing = models.BooleanField(default=False)

    target_runs = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Target runs for chase (if applicable)"
    )

    revised_target_runs = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="DLS / manual revised target"
    )

    max_overs = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Revised max overs for innings (interruptions)"
    )

    target_achieved = models.BooleanField(default=False)

    # Current state snapshot
    current_striker = models.ForeignKey(
        Player,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+"
    )

    current_non_striker = models.ForeignKey(
        Player,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+"
    )

    current_bowler = models.ForeignKey(
        Player,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+"
    )

    # Last processed ball (for resume / undo)
    last_ball = models.ForeignKey(
        Ball,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+"
    )

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Aggregate for Innings {self.innings_id}"
