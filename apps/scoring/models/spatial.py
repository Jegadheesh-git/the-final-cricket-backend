import uuid
from django.db import models
from scoring.models import Ball

class BallSpatialOutcome(models.Model):
    """
    Spatial outcome of a delivery:
    - Shot impact location
    - Wagon wheel direction
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    ball = models.OneToOneField(
        Ball,
        on_delete=models.CASCADE,
        related_name="spatial_outcome"
    )

    # 🟫 Shot impact on pitch (normalized coordinates)
    shot_zone_x = models.FloatField(
        null=True,
        blank=True,
        help_text="Normalized X coordinate of shot impact on pitch"
    )
    shot_zone_y = models.FloatField(
        null=True,
        blank=True,
        help_text="Normalized Y coordinate of shot impact on pitch"
    )

    # 🧭 Wagon wheel direction (normalized coordinates)
    wagon_wheel_x = models.FloatField(
        null=True,
        blank=True,
        help_text="Normalized X coordinate for wagon wheel"
    )
    wagon_wheel_y = models.FloatField(
        null=True,
        blank=True,
        help_text="Normalized Y coordinate for wagon wheel"
    )

    # Pitch and stump zones (categorical)
    pitch_zone = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Pitch zone selected from matrix"
    )
    stump_zone = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        help_text="Stump zone selected from matrix"
    )

    # Structured field engine selection
    structured_region_id = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        help_text="Structured field engine region id"
    )
    structured_slice_index = models.PositiveSmallIntegerField(
        null=True,
        blank=True
    )
    structured_band_index = models.PositiveSmallIntegerField(
        null=True,
        blank=True
    )
    structured_position = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Resolved fielding position from structured engine"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["ball"]),
        ]

    def __str__(self):
        return f"Spatial outcome for Ball {self.ball_id}"
