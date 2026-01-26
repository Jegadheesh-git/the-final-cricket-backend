import uuid
from django.db import models
from scoring.models import Ball

class BallTrajectory(models.Model):
    """
    Time-sequenced tracking points for a ball's flight.
    Multiple rows per ball, ordered by sequence_index.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    ball = models.ForeignKey(
        Ball,
        on_delete=models.CASCADE,
        related_name="trajectory_points"
    )

    # Ordering within the trajectory
    sequence_index = models.PositiveIntegerField(
        help_text="Order of this point in the trajectory sequence"
    )

    # Normalized spatial coordinates
    x = models.FloatField(
        help_text="Normalized X coordinate of the ball"
    )
    y = models.FloatField(
        help_text="Normalized Y coordinate of the ball"
    )
    z = models.FloatField(
        null=True,
        blank=True,
        help_text="Optional Z coordinate (height)"
    )

    # Optional timestamp relative to ball release (ms)
    time_ms = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Milliseconds since ball release"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sequence_index"]
        unique_together = (
            ("ball", "sequence_index"),
        )
        indexes = [
            models.Index(fields=["ball", "sequence_index"]),
        ]

    def __str__(self):
        return f"Trajectory point {self.sequence_index} for Ball {self.ball_id}"
