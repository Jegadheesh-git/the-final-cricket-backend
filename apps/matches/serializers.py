from rest_framework import serializers
from .models import Match
from coredata.models import Team 

class MatchCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = (
            "id",
            "competition",
            "series",
            "match_type",
            "team1",
            "team2",
            "stadium",
            "match_date",
            "start_time",
            "match_mode",
        )
    def validate(self, data):
        competition = data.get("competition")
        series = data.get("series")
        # XOR check
        if bool(competition) == bool(series):
            raise serializers.ValidationError(
                "Match must belong to either competition or series"
            )
        if data["team1"] == data["team2"]:
            raise serializers.ValidationError("Teams must be different")
        return data

class PlayingXIInputSerializer(serializers.Serializer):
    team_id = serializers.UUIDField()
    players = serializers.ListField(
        child=serializers.DictField(),
        allow_empty=False
    )
    def validate_players(self, players):
        if len(players) != 11:
            raise serializers.ValidationError("Exactly 11 players required")
        positions = [p.get("batting_position") for p in players]
        if sorted(positions) != list(range(1, 12)):
            raise serializers.ValidationError(
                "batting_position must be 1 to 11"
            )
        captains = [p for p in players if p.get("is_captain")]
        if len(captains) != 1:
            raise serializers.ValidationError(
                "Exactly one captain required"
            )
        return players

class TossCreateSerializer(serializers.Serializer):
    won_by = serializers.UUIDField()
    decision = serializers.ChoiceField(
        choices=(
            ("BAT", "Bat"),
            ("BOWL", "Bowl"),
        )
    )

class InningsCreateSerializer(serializers.Serializer):
    batting_team = serializers.UUIDField()

class TeamMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ("id", "name")


class MatchDetailSerializer(serializers.ModelSerializer):
    competition = serializers.PrimaryKeyRelatedField(read_only=True)
    series = serializers.PrimaryKeyRelatedField(read_only=True)

    team1 = TeamMiniSerializer(read_only=True)
    team2 = TeamMiniSerializer(read_only=True)

    class Meta:
        model = Match
        fields = (
            "id",
            "competition",
            "series",
            "team1",
            "team2",
            "state"
        )