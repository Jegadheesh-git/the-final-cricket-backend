from django.db import models
import uuid

class Nationality(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=3, unique=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name + " - " + self.code
    
class OwnedModel(models.Model):
    """
    Base model for SYSTEM + USER + ORG owned master data
    """

    OWNER_TYPE_CHOICES = (
        ("SYSTEM","System"),
        ("USER","User"),
        ("ORG","Organization")
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    owner_type = models.CharField(
        max_length=10,
        choices=OWNER_TYPE_CHOICES,
        default="SYSTEM"
    )

    owner_id = models.UUIDField(null=True, blank=True)

    is_locked = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

class Stadium(OwnedModel):
    name = models.CharField(max_length=150)
    city = models.CharField(max_length=100)

    nationality = models.ForeignKey(
        Nationality,
        on_delete = models.PROTECT,
        related_name="stadiums" 
    )

    class Meta:
        unique_together = (
            "name",
            "city",
            "nationality"
        )

        ordering = ["name"]

    def __str__(self):
        return f"{self.name}, {self.city} - {self.nationality}"


class Umpire(OwnedModel):
    name = models.CharField(max_length=150)
    nationality = models.ForeignKey(
        Nationality,
        on_delete = models.PROTECT,
        related_name="umpires" 
    )

    class Meta:
        unique_together = (
            "name",
            "nationality",
            "owner_type",
            "owner_id"
        )

        ordering = ["name"]

    def __str__(self):
        return f"{self.name} - {self.nationality}"

class Player(OwnedModel):
    # ---- Identity ----
    ci_player_id = models.CharField(max_length=100, blank=True, default="")
    jersey_number = models.CharField(max_length=20, blank=True, default="")
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    nick_name = models.CharField(max_length=100, blank=True)
    nationality = models.ForeignKey(
        Nationality,
        on_delete=models.PROTECT,
        related_name="players"
    )
    date_of_birth = models.DateField(null=True, blank=True)
    GENDER_CHOICES = (
        ("MALE", "Male"),
        ("FEMALE", "Female"),
        ("OTHER", "Other"),
    )
    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES
    )
    # ---- Physical ----
    height_cm = models.PositiveIntegerField(null=True, blank=True)
    weight_kg = models.PositiveIntegerField(null=True, blank=True)
    # ---- Handedness ----
    HAND_CHOICES = (
        ("LEFT", "Left"),
        ("RIGHT", "Right"),
    )
    batting_hand = models.CharField(
        max_length=5,
        choices=HAND_CHOICES,
        null=True, blank=True
    )
    bowling_hand = models.CharField(
        max_length=5,
        choices=HAND_CHOICES,
        null=True, blank=True
    )
    # ---- Role ----
    ROLE_CHOICES = (
        ("BATTER", "Batter"),
        ("BOWLER", "Bowler"),
        ("ALL_ROUNDER", "All Rounder"),
        ("WICKET_KEEPER", "Wicket Keeper"),
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        null=True, blank=True
    )
    # ---- Skill classification ----
    BOWLING_TYPE_CHOICES = (
        ("PACE", "Pace"),
        ("MEDIUM", "Medium Pace"),
        ("SPIN", "Spin"),
    )
    bowling_type = models.CharField(
        max_length=10,
        choices=BOWLING_TYPE_CHOICES,
        null=True,
        blank=True
    )
    BATTING_TYPE_CHOICES = (
        ("AGGRESSIVE", "Aggressive"),
        ("ANCHOR", "Anchor"),
        ("FINISHER", "Finisher"),
    )
    batting_type = models.CharField(
        max_length=15,
        choices=BATTING_TYPE_CHOICES,
        null=True,
        blank=True
    )
    # ---- Descriptive styles ----
    batting_style = models.CharField(
        max_length=100,
        blank=True
    )
    bowling_style = models.CharField(
        max_length=100,
        blank=True
    )
    # ---- Advanced skills (structured) ----
    fielding_attributes = models.JSONField(default=dict)
    wicket_keeping_skill = models.JSONField(default=dict)
    class Meta:
        ordering = ["last_name", "first_name"]
        indexes = [
            models.Index(fields=["last_name", "first_name"]),
            models.Index(fields=["nationality", "role"]),
        ]
    
    def __str__(self):
        return f"{self.last_name}, {self.first_name} - {self.nationality}"

class Team(OwnedModel):
    TEAM_TYPE_CHOICES = (
        ("INTERNATIONAL", "International"),
        ("DOMESTIC", "Domestic"),
        ("LEAGUE", "League"),
    )
    name = models.CharField(max_length=150)
    short_name = models.CharField(max_length=20)
    team_type = models.CharField(
        max_length=20,
        choices=TEAM_TYPE_CHOICES
    )
    nationality = models.ForeignKey(
        Nationality,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="teams"
    )
    class Meta:
        unique_together = (
            "name",
            "owner_type",
            "owner_id",
        )
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["team_type"]),
        ]
    def __str__(self):
        return self.name










