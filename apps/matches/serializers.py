from rest_framework import serializers
from .models import Match, MatchType
from coredata.models import Team

class MatchTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchType
        fields = ('id','name','code')

class MatchCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = (
            "id",
            "ci_id",
            "competition",
            "series",
            "match_type",
            "team1",
            "team2",
            "stadium",
            "match_date",
            "start_time",
            "drs_count",
            "floodlights_count",
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

    team1_id = serializers.CharField(source="team1.id", read_only=True)
    team2_id = serializers.CharField(source="team2.id", read_only=True)

    team1_name = serializers.CharField(source="team1.name", read_only=True)
    team2_name = serializers.CharField(source="team2.name", read_only=True)

    competition = serializers.CharField(source="competition.id", read_only=True)

    match_type_name = serializers.CharField(
        source="match_type.name",
        read_only=True
    )
    match_label = serializers.SerializerMethodField()

    class Meta:
        model = Match
        fields = (
            "id",
            "match_label",
            "match_type_name",
            "match_mode",
            "team1_id",
            "team2_id",
            "team1_name",
            "team2_name",
            "competition",
            "match_date",
            "ci_id",
            "drs_count",
            "floodlights_count",
            "state",
        )

    def get_match_label(self, obj):
        """
        Example:
        India vs Australia on 2026-01-28 (World Cup)
        India vs Australia on 2026-01-28 (CASUAL)
        """
        if obj.competition:
            context = obj.competition.name
        elif obj.series:
            context = obj.series.name
        else:
            context = "CASUAL"

        return f"{obj.team1.name} vs {obj.team2.name} on {obj.match_date} ({context})"
