import uuid
from django.db import models
from scoring.models import Ball

class BallVideo(models.Model):
    """
    Video segment corresponding to a specific ball.
    Used for replay, highlights, and analysis.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    ball = models.OneToOneField(
        Ball,
        on_delete=models.CASCADE,
        related_name="video"
    )

    # 🎥 Video reference (logical, not storage)
    video_source_id = models.CharField(
        max_length=100,
        help_text="Identifier for the match video source"
    )

    # ⏱ Time range in milliseconds
    video_start_ms = models.PositiveIntegerField(
        help_text="Start timestamp of the ball in milliseconds"
    )

    video_end_ms = models.PositiveIntegerField(
        help_text="End timestamp of the ball in milliseconds"
    )

    # Optional metadata
    camera_angle = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Broadcast / end-on / side-on etc."
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["video_source_id"]),
            models.Index(fields=["ball"]),
        ]

    def __str__(self):
        return f"Video for Ball {self.ball_id} [{self.video_start_ms}-{self.video_end_ms}]"
