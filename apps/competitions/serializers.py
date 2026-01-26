from rest_framework import serializers
from coredata.serializers import OwnedModelSerializer
from .models import Tournament, Competition, CompetitionTeam

class TournamentSerializer(OwnedModelSerializer):
    class Meta:
        model = Tournament
        fields = (
            "id",
            "name",
            "short_name",
            "tournament_type",
            "nationality",
            "owner_type",
            "owner_id",
            "is_locked",
            "is_active",
        )


class CompetitionSerializer(OwnedModelSerializer):
    class Meta:
        model = Competition
        fields = (
            "id",
            "name",
            "tournament",
            "season",
            "start_date",
            "end_date",
            "owner_type",
            "owner_id",
            "is_locked",
            "is_active",
        )

class CompetitionTeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompetitionTeam
        fields = (
            "id",
            "competition",
            "team",
            "added_at",
        )
        read_only_fields = ("added_at",)

class CompetitionTeamBulkInputSerializer(serializers.Serializer):
    team_ids = serializers.ListField(
        child=serializers.UUIDField(),
        allow_empty=False,
    )

class CompetitionSquadBulkInputSerializer(serializers.Serializer):
    player_ids = serializers.ListField(
        child=serializers.UUIDField(),
        allow_empty=False,
    )

class SeriesTeamBulkInputSerializer(serializers.Serializer):
    team_ids = serializers.ListField(
        child=serializers.UUIDField(),
        allow_empty=False,
    )

class SeriesSquadBulkInputSerializer(serializers.Serializer):
    player_ids = serializers.ListField(
        child=serializers.UUIDField(),
        allow_empty=False,
    )





