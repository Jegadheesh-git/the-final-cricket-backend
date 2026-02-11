import uuid
from django.db import models
from django.core.exceptions import ValidationError
from coredata.models import Team, Stadium, Umpire, Player, OwnedModel
from competitions.models import Competition, Series

class MatchType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)           # ODI, T20, Test, Hundred
    code = models.CharField(max_length=20)           # ODI, T20, TEST, HUNDRED
    balls_per_over = models.PositiveSmallIntegerField(default=6)
    max_overs = models.PositiveSmallIntegerField(null=True, blank=True)  # None for Test
    max_innings = models.PositiveSmallIntegerField(default=2)
    allow_super_over = models.BooleanField(default=False)
    allow_draw = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    class Meta:
        unique_together = ("code",)
        ordering = ["name"]
    def __str__(self):
        return self.name + "( " + str(self.id) + " )"

    @property
    def is_test(self):
        return self.code == "TEST"

    @property
    def follow_on_allowed(self):
        return self.is_test

    @property
    def super_over_allowed(self):
        return self.allow_super_over

class Match(OwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ci_id = models.CharField(max_length=100, blank=True, default="")
    drs_count = models.PositiveSmallIntegerField(null=True, blank=True)
    floodlights_count = models.PositiveSmallIntegerField(null=True, blank=True)
    # Context (exactly ONE must be set)
    competition = models.ForeignKey(
        Competition,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="matches"
    )
    series = models.ForeignKey(
        Series,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="matches"
    )
    match_type = models.ForeignKey(
        MatchType,
        on_delete=models.PROTECT
    )
    team1 = models.ForeignKey(
        Team,
        on_delete=models.PROTECT,
        related_name="matches_as_team1"
    )
    team2 = models.ForeignKey(
        Team,
        on_delete=models.PROTECT,
        related_name="matches_as_team2"
    )
    stadium = models.ForeignKey(
        Stadium,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
    umpires = models.ManyToManyField(
        Umpire,
        blank=True
    )
    match_date = models.DateField(null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    # EXECUTION MODE
    MATCH_MODE_CHOICES = (
        ("ONLINE", "Online"),
        ("OFFLINE", "Offline"),
    )
    match_mode = models.CharField(
        max_length=10,
        choices=MATCH_MODE_CHOICES
    )
    # STATE MACHINE
    STATE_CHOICES = (
        ("DRAFT", "Draft"),
        ("READY", "Ready"),
        ("IN_PROGRESS", "In Progress"),
        ("COMPLETED", "Completed"),
    )
    state = models.CharField(
        max_length=20,
        choices=STATE_CHOICES,
        default="DRAFT"
    )
    # Offline safety
    offline_snapshot_hash = models.CharField(
        max_length=64,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        indexes = [
            models.Index(fields=["competition"]),
            models.Index(fields=["series"]),
            models.Index(fields=["state"]),
            models.Index(fields=["match_mode"]),
        ]
    def clean(self):
        # Must belong to exactly one context
        if bool(self.competition) == bool(self.series):
            raise ValidationError(
                "Match must belong to either competition or series"
            )
        if self.team1 == self.team2:
            raise ValidationError("Teams must be different")
    def __str__(self):
        return f"{self.team1} vs {self.team2}"

class PlayingXI(models.Model):
    match = models.ForeignKey(
        Match,
        on_delete=models.CASCADE,
        related_name="playing_xis"
    )
    team = models.ForeignKey(
        Team,
        on_delete=models.PROTECT
    )
    player = models.ForeignKey(
        Player,
        on_delete=models.PROTECT
    )
    batting_position = models.PositiveSmallIntegerField()  # 1–11
    is_captain = models.BooleanField(default=False)
    is_wicket_keeper = models.BooleanField(default=False)
    class Meta:
        unique_together = ("match", "team", "player")
        ordering = ["batting_position"]
        indexes = [
            models.Index(fields=["match", "team"]),
        ]

class Toss(models.Model):
    match = models.OneToOneField(
        Match,
        on_delete=models.CASCADE,
        related_name="toss"
    )
    won_by = models.ForeignKey(
        Team,
        on_delete=models.PROTECT,
        related_name="tosses_won"
    )
    decision = models.CharField(
        max_length=10,
        choices=(
            ("BAT", "Bat"),
            ("BOWL", "Bowl"),
        )
    )
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        indexes = [
            models.Index(fields=["match"]),
        ]
    def __str__(self):
        return f"Toss: {self.won_by} chose {self.decision}"
        
class Innings(models.Model):
    """
    Structural container for an innings.
    Holds NO scoring data.
    """

    class State(models.TextChoices):
        OPEN = "OPEN", "Open"
        ACTIVE = "ACTIVE", "Active"
        COMPLETED = "COMPLETED", "Completed"
        ABANDONED = "ABANDONED", "Abandoned"

    match = models.ForeignKey(
        Match,
        on_delete=models.CASCADE,
        related_name="innings"
    )

    innings_number = models.PositiveSmallIntegerField(
        help_text="Sequential innings number within the match"
    )

    batting_team = models.ForeignKey(
        Team,
        on_delete=models.PROTECT,
        related_name="innings_batted"
    )

    bowling_team = models.ForeignKey(
        Team,
        on_delete=models.PROTECT,
        related_name="innings_bowled"
    )

    # Lifecycle
    state = models.CharField(
        max_length=12,
        choices=State.choices,
        default=State.OPEN
    )

    # Special innings flags
    is_super_over = models.BooleanField(
        default=False,
        help_text="True if this innings is a super over"
    )

    super_over_index = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="1,2,3... if super over"
    )

    start_time = models.DateTimeField(
        null=True,
        blank=True
    )

    end_time = models.DateTimeField(
        null=True,
        blank=True
    )

    class Meta:
        unique_together = ("match", "innings_number")
        ordering = ["innings_number"]
        indexes = [
            models.Index(fields=["match", "innings_number"]),
            models.Index(fields=["match", "state"]),
        ]

    def __str__(self):
        label = f"Innings {self.innings_number}"
        if self.is_super_over:
            label += f" (Super Over {self.super_over_index})"
        return f"{label} - {self.batting_team}"

