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
            "nationality",
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
            "team_type",
            "nationality",
            "owner_type",
            "is_locked",
        )

        read_only_fields = (
            "owner_type",
            "is_locked",
        )