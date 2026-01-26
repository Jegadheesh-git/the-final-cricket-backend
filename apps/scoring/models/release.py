import uuid
from django.db import models
from scoring.models import Ball

class BallReleaseData(models.Model):
    """
    Positional data captured at the moment of ball release.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    ball = models.OneToOneField(
        Ball,
        on_delete=models.CASCADE,
        related_name="release_data"
    )

    # 🎯 Bowler release coordinates (normalized)
    bowler_release_x = models.FloatField(
        null=True,
        blank=True,
        help_text="Normalized X coordinate of bowler release point"
    )

    bowler_release_y = models.FloatField(
        null=True,
        blank=True,
        help_text="Normalized Y coordinate of bowler release point"
    )

    bowler_release_position = models.CharField(
        max_length=30,
        null=True,
        blank=True,
        help_text="Encoded release position (wide/close/over/round arm etc.)"
    )

    # 🧤 Wicket keeper stance
    wicket_keeper_position = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        help_text="Standing up / back"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["ball"]),
            models.Index(fields=["bowler_release_position"]),
        ]

    def __str__(self):
        return f"Release data for Ball {self.ball_id}"
