import uuid
from django.db import models
from coredata.models import Nationality, OwnedModel, Team, Player

class Tournament(OwnedModel):
    name = models.CharField(max_length=150)
    short_name = models.CharField(max_length=50)
    ci_id = models.CharField(max_length=100, blank=True, default="")
    established_year = models.PositiveSmallIntegerField(null=True, blank=True)
    end_year = models.PositiveSmallIntegerField(null=True, blank=True)
    TOURNAMENT_TYPE_CHOICES = (
        ("INTERNATIONAL", "International"),
        ("DOMESTIC", "Domestic"),
        ("LEAGUE", "League"),
        ("SCHOOL", "School"),
        ("CLUB", "Club"),
    )
    tournament_type = models.CharField(
        max_length=20,
        choices=TOURNAMENT_TYPE_CHOICES
    )
    nationality = models.ForeignKey(
        Nationality,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="tournaments"
    )
    is_active = models.BooleanField(default=True)
    class Meta:
        unique_together = (
            "name",
            "owner_type",
            "owner_id",
        )
        ordering = ["name"]
        indexes = [
            models.Index(fields=["tournament_type"]),
            models.Index(fields=["nationality"]),
        ]
    def __str__(self):
        return self.name

class Competition(OwnedModel):
    name = models.CharField(max_length=150)
    ci_id = models.CharField(max_length=100, blank=True, default="")
    # Optional link to tournament
    tournament = models.ForeignKey(
        Tournament,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="competitions"
    )
    season = models.CharField(
        max_length=50,
        blank=True,
        help_text="Season or year, e.g. 2024, 2024-25"
    )
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    established_year = models.PositiveSmallIntegerField(null=True, blank=True)
    end_year = models.PositiveSmallIntegerField(null=True, blank=True)
    teams = models.ManyToManyField(
        Team,
        through="CompetitionTeam",
        related_name="competitions",
        blank=True,
    )
    is_active = models.BooleanField(default=True)
    is_locked = models.BooleanField(default=False)
    class Meta:
        unique_together = (
            "name",
            "owner_type",
            "owner_id",
        )
        ordering = ["-start_date", "name"]
        indexes = [
            models.Index(fields=["start_date"]),
            models.Index(fields=["owner_type", "owner_id"]),
        ]
    def __str__(self):
        return self.name

class CompetitionTeam(models.Model):
    competition = models.ForeignKey(
        Competition,
        on_delete=models.CASCADE,
        related_name="competition_teams"
    )
    team = models.ForeignKey(
        Team,
        on_delete=models.PROTECT,
        related_name="competition_entries"
    )

    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (
            "competition",
            "team",
        )
        ordering = ["team__name"]
        indexes = [
            models.Index(fields=["competition"]),
            models.Index(fields=["team"]),
        ]

    def __str__(self):
        return f"{self.team.name} - {self.competition.name}"


class CompetitionSquad(models.Model):
    competition_team = models.ForeignKey(
        CompetitionTeam,
        on_delete=models.CASCADE,
        related_name="squad"
    )
    player = models.ForeignKey(
        Player,
        on_delete=models.PROTECT,
        related_name="competition_squads"
    )
    added_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ("competition_team", "player")
        ordering = ["player__last_name", "player__first_name"]
        indexes = [
            models.Index(fields=["competition_team"]),
            models.Index(fields=["player"]),
        ]
    def __str__(self):
        return f"{self.player} @ {self.competition_team}"

class Series(OwnedModel):

    name = models.CharField(max_length=150)
    ci_id = models.CharField(max_length=100, blank=True, default="")
    SERIES_TYPE_CHOICES = (
        ("BILATERAL", "Bilateral"),
        ("TRI", "Tri-series"),
        ("MULTI", "Multi-team"),
        ("FRIENDLY", "Friendly"),
        ("PRACTICE", "Practice"),
    )
    series_type = models.CharField(
        max_length=20,
        choices=SERIES_TYPE_CHOICES
    )
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    established_year = models.PositiveSmallIntegerField(null=True, blank=True)
    end_year = models.PositiveSmallIntegerField(null=True, blank=True)
    teams = models.ManyToManyField(
        Team,
        through="SeriesTeam",
        related_name="series",
        blank=True,
    )
    is_active = models.BooleanField(default=True)
    is_locked = models.BooleanField(default=False)  # :lock: critical
    class Meta:
        unique_together = ("name", "owner_type", "owner_id")
        ordering = ["-start_date", "name"]
        indexes = [
            models.Index(fields=["series_type"]),
            models.Index(fields=["owner_type", "owner_id"]),
        ]
    def __str__(self):
        return self.name

class SeriesTeam(models.Model):
    series = models.ForeignKey(
        Series,
        on_delete=models.CASCADE,
        related_name="series_teams"
    )
    team = models.ForeignKey(
        Team,
        on_delete=models.PROTECT,
        related_name="series_entries"
    )
    added_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ("series", "team")
        ordering = ["team__name"]
        indexes = [
            models.Index(fields=["series"]),
            models.Index(fields=["team"]),
        ]
    def __str__(self):
        return f"{self.team.name} @ {self.series.name}"

class SeriesSquad(models.Model):
    series_team = models.ForeignKey(
        SeriesTeam,
        on_delete=models.CASCADE,
        related_name="squad"
    )
    player = models.ForeignKey(
        Player,
        on_delete=models.PROTECT,
        related_name="series_squads"
    )
    added_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ("series_team", "player")
        ordering = ["player__last_name", "player__first_name"]
        indexes = [
            models.Index(fields=["series_team"]),
            models.Index(fields=["player"]),
        ]
    def __str__(self):
        return f"{self.player} @ {self.series_team}"
