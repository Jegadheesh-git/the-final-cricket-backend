import uuid
from django.db import models
from scoring.models import Ball

class BallAnalytics(models.Model):
    """
    Optional qualitative analytics for a delivery.
    Used for broadcast graphics, AI, and performance analysis.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    ball = models.OneToOneField(
        Ball,
        on_delete=models.CASCADE,
        related_name="analytics"
    )

    # 🏏 Delivery characteristics
    delivery_type = models.CharField(
        max_length=30,
        null=True,
        blank=True,
        help_text="Yorker, bouncer, good length, full toss, etc."
    )

    crease_movement = models.CharField(
        max_length=30,
        null=True,
        blank=True,
        help_text="Bowler movement on the crease"
    )

    # 🏏 Batting interaction
    shot_connection = models.CharField(
        max_length=30,
        null=True,
        blank=True,
        help_text="Early / Late / Perfect timing"
    )

    bat_subject = models.CharField(
        max_length=30,
        null=True,
        blank=True,
        help_text="Edge / Middle / Toe / Handle"
    )

    stroke = models.CharField(
        max_length=30,
        null=True,
        blank=True,
        help_text="Drive, cut, pull, sweep, etc."
    )

    # 🧤 Fielding & keeper actions
    keeper_activity = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Keeper movement or action"
    )

    fielding_activity = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Fielding action involved"
    )

    # 👤 Batter movement
    batsman_activity = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Footwork, trigger movement"
    )

    # 🧑‍⚖️ Umpire-related (optional)
    umpire_activity = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Signal, position, interaction"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["delivery_type"]),
            models.Index(fields=["stroke"]),
        ]

    def __str__(self):
        return f"Analytics for Ball {self.ball_id}"
