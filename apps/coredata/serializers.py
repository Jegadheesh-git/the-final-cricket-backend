from rest_framework import serializers
from .models import Nationality, Stadium, Umpire, Player, Team

class NationalitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Nationality
        fields = ("id","name","code")

class OwnedModelSerializer(serializers.ModelSerializer):
    owner_type = serializers.CharField(read_only=True)
    owner_id = serializers.UUIDField(read_only=True)
    is_locked = serializers.BooleanField(read_only=True)

    class Meta:
        abstract = True

class StadiumSerializer(OwnedModelSerializer):
    class Meta:
        model = Stadium
        fields = (
            "id",
            "name",
            "city",
            "ci_id",
            "specific_area",
            "established_year",
            "floodlights",
            "time_zone",
            "nationality",
            "home_teams",
            "owner_type",
            "is_locked",
        )

        read_only_fields = (
            "owner_type",
            "is_locked",
        )


class UmpireSerializer(OwnedModelSerializer):
    class Meta:
        model = Umpire
        fields = (
            "id",
            "name",
            "last_name",
            "short_name",
            "ci_id",
            "date_of_birth",
            "nationality",
            "owner_type",
            "is_locked",
        )

        read_only_fields = (
            "owner_type",
            "is_locked",
        )

class PlayerSerializer(OwnedModelSerializer):
    class Meta:
        model = Player
        fields = (
            "id",
            "ci_player_id",
            "jersey_number",
            "debut_year_intl",
            "retirement_year_intl",
            "first_name",
            "middle_name",
            "last_name",
            "nick_name",
            "date_of_birth",
            "gender",
            "height_cm",
            "weight_kg",
            "batting_hand",
            "bowling_hand",
            "role",
            "bowling_type",
            "bowling_types",
            "batting_type",
            "batting_style",
            "bowling_style",
            "fielding_attributes",
            "wicket_keeping_skill",
            "nationality",
            "owner_type",
            "is_locked",
        )

        read_only_fields = (
            "owner_type",
            "is_locked",
        )

class TeamSerializer(OwnedModelSerializer):
    class Meta:
        model = Team
        fields = (
            "id",
            "name",
            "short_name",
            "ci_id",
            "team_category",
            "established_year",
            "team_type",
            "nationality",
            "master_squad",
            "owner_type",
            "is_locked",
        )

        read_only_fields = (
            "owner_type",
            "is_locked",
        )
