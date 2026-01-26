from django.db import transaction
import uuid
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError, PermissionDenied
from backend.core.viewsets import OwnedModelViewSet, OwnedModelListView
from .models import Tournament, Competition, CompetitionTeam, CompetitionSquad
from coredata.models import Team, Player
from .serializers import (
    TournamentSerializer, CompetitionSerializer, 
    CompetitionTeamBulkInputSerializer, CompetitionSquadBulkInputSerializer,
    SeriesTeamBulkInputSerializer, SeriesSquadBulkInputSerializer
)
from django.shortcuts import get_object_or_404

class TournamentViewSet(OwnedModelViewSet):
    queryset = Tournament.objects.all()
    serializer_class = TournamentSerializer

class TournamentListView(OwnedModelListView):
    queryset = Tournament.objects.all()
    serializer_class = TournamentSerializer

class CompetitionViewSet(OwnedModelViewSet):
    queryset = Competition.objects.all()
    serializer_class = CompetitionSerializer

class CompetitionListView(OwnedModelListView):
    queryset = Competition.objects.all()
    serializer_class = CompetitionSerializer

def validate_competition_editable(request, competition):
    scope = request.scope
    check_id = scope.owner_id
    if isinstance(check_id, int) and isinstance(competition.owner_id, uuid.UUID):
        try:
            check_id = uuid.UUID(int=check_id)
        except ValueError:
            pass

    if competition.owner_type != scope.owner_type or competition.owner_id != check_id:
        raise PermissionDenied("Competition does not belong to you")
    if competition.is_locked:
        raise ValidationError("Competition is locked")
    # later:
    # if competition.matches.exists():
    #     raise ValidationError("Competition already has matches")

def validate_squad_editable(request, competition_team):
    competition = competition_team.competition
    scope = request.scope
    check_id = scope.owner_id
    if isinstance(check_id, int) and isinstance(competition.owner_id, uuid.UUID):
        try:
            check_id = uuid.UUID(int=check_id)
        except ValueError:
            pass
            
    if competition.owner_type != scope.owner_type or competition.owner_id != check_id:
        raise PermissionDenied("Competition does not belong to you")
    if competition.is_locked:
        raise ValidationError("Competition is locked")
    # later:
    # if competition.matches.exists():
    #     raise ValidationError("Matches already exist")


class CompetitionTeamsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, competition_id):
        competition = Competition.objects.get(id=competition_id)
        validate_competition_editable(request, competition)
        entries = CompetitionTeam.objects.filter(
            competition=competition
        ).select_related("team")
        return Response({
            "competition_id": competition.id,
            "is_locked": competition.is_locked,
            "teams": [
                {
                    "id": entry.team.id,
                    "name": entry.team.name,
                    "short_name": entry.team.short_name,
                }
                for entry in entries
            ]
        })

    def post(self, request, competition_id):
        serializer = CompetitionTeamBulkInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        competition = Competition.objects.get(id=competition_id)
        validate_competition_editable(request, competition)
        team_ids = serializer.validated_data["team_ids"]
        teams = Team.objects.filter(id__in=team_ids)
        if teams.count() != len(team_ids):
            raise ValidationError("Invalid team id provided")
        scope = request.scope
        with transaction.atomic():
            for team in teams:
                if team.owner_type == "SYSTEM" and not scope.allow_system_data:
                    raise ValidationError("System teams not allowed")
                CompetitionTeam.objects.get_or_create(
                    competition=competition,
                    team=team
                )
        return Response({"status": "teams added"})

    def put(self, request, competition_id):
        serializer = CompetitionTeamBulkInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        competition = Competition.objects.get(id=competition_id)
        validate_competition_editable(request, competition)
        new_team_ids = set(serializer.validated_data["team_ids"])
        teams = Team.objects.filter(id__in=new_team_ids)
        if teams.count() != len(new_team_ids):
            raise ValidationError("Invalid team id provided")
        existing = CompetitionTeam.objects.filter(competition=competition)
        existing_ids = set(existing.values_list("team_id", flat=True))
        to_add = new_team_ids - existing_ids
        to_remove = existing_ids - new_team_ids
        scope = request.scope
        with transaction.atomic():
            for team in teams:
                if team.id in to_add:
                    if team.owner_type == "SYSTEM" and not scope.allow_system_data:
                        raise ValidationError("System teams not allowed")
                    CompetitionTeam.objects.create(
                        competition=competition,
                        team=team
                    )
            CompetitionTeam.objects.filter(
                competition=competition,
                team_id__in=to_remove
            ).delete()
        return Response({"status": "teams replaced"})

class CompetitionSquadView(APIView):
    permission_classes = [IsAuthenticated]

    def _get_competition_team(self, competition_id, team_id):
        return get_object_or_404(
            CompetitionTeam,
            competition_id=competition_id,
            team_id=team_id,
        )

    def get(self, request, competition_id, team_id):
        competition_team = self._get_competition_team(
            competition_id, team_id
        )

        validate_squad_editable(request, competition_team)

        squad = (
            CompetitionSquad.objects
            .filter(competition_team=competition_team)
            .select_related("player")
        )

        return Response({
            "competition_team_id": competition_team.id,
            "is_locked": competition_team.competition.is_locked,
            "players": [
                {
                    "id": entry.player.id,
                    "first_name": entry.player.first_name,
                    "last_name": entry.player.last_name,
                    "role": entry.player.role,
                }
                for entry in squad
            ]
        })

    def post(self, request, competition_id, team_id):
        serializer = CompetitionSquadBulkInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        competition_team = self._get_competition_team(
            competition_id, team_id
        )

        validate_squad_editable(request, competition_team)

        player_ids = serializer.validated_data["player_ids"]
        players = Player.objects.filter(id__in=player_ids)

        if players.count() != len(player_ids):
            raise ValidationError("Invalid player id provided")

        scope = request.scope

        with transaction.atomic():
            for player in players:
                if player.owner_type == "SYSTEM" and not scope.allow_system_data:
                    raise ValidationError("System players not allowed")

                CompetitionSquad.objects.get_or_create(
                    competition_team=competition_team,
                    player=player
                )

        return Response({"status": "players added"})

    def put(self, request, competition_id, team_id):
        serializer = CompetitionSquadBulkInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        competition_team = self._get_competition_team(
            competition_id, team_id
        )

        validate_squad_editable(request, competition_team)

        new_player_ids = set(serializer.validated_data["player_ids"])
        players = Player.objects.filter(id__in=new_player_ids)

        if players.count() != len(new_player_ids):
            raise ValidationError("Invalid player id provided")

        existing = CompetitionSquad.objects.filter(
            competition_team=competition_team
        )

        existing_ids = set(existing.values_list("player_id", flat=True))
        to_add = new_player_ids - existing_ids
        to_remove = existing_ids - new_player_ids

        scope = request.scope

        with transaction.atomic():
            for player in players:
                if player.id in to_add:
                    if player.owner_type == "SYSTEM" and not scope.allow_system_data:
                        raise ValidationError("System players not allowed")

                    CompetitionSquad.objects.create(
                        competition_team=competition_team,
                        player=player
                    )

            CompetitionSquad.objects.filter(
                competition_team=competition_team,
                player_id__in=to_remove
            ).delete()

        return Response({"status": "squad replaced"})


def validate_series_editable(request, series):
    scope = request.scope

    if series.owner_type != scope.owner_type or series.owner_id != scope.owner_id:
        raise ValidationError("You are not allowed to edit this series")
    
    if series.is_locked:
        raise ValidationError("This series is locked")

class SeriesTeamsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, series_id):
        series = Series.objects.get(id=series_id)
        validate_series_editable(request, series)
        entries = SeriesTeam.objects.filter(
            series=series
        ).select_related("team")
        return Response({
            "series_id": series.id,
            "is_locked": series.is_locked,
            "teams": [
                {
                    "id": entry.team.id,
                    "name": entry.team.name,
                    "short_name": entry.team.short_name,
                }
                for entry in entries
            ]
        })
    def post(self, request, series_id):
        serializer = SeriesTeamBulkInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        series = Series.objects.get(id=series_id)
        validate_series_editable(request, series)
        team_ids = serializer.validated_data["team_ids"]
        teams = Team.objects.filter(id__in=team_ids)
        if teams.count() != len(team_ids):
            raise ValidationError("Invalid team id provided")
        scope = request.scope
        with transaction.atomic():
            for team in teams:
                if team.owner_type == "SYSTEM" and not scope.allow_system_data:
                    raise ValidationError("System teams not allowed")
                SeriesTeam.objects.get_or_create(
                    series=series,
                    team=team
                )
        return Response({"status": "teams added"})
    def put(self, request, series_id):
        serializer = SeriesTeamBulkInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        series = Series.objects.get(id=series_id)
        validate_series_editable(request, series)
        new_team_ids = set(serializer.validated_data["team_ids"])
        teams = Team.objects.filter(id__in=new_team_ids)
        if teams.count() != len(new_team_ids):
            raise ValidationError("Invalid team id provided")
        existing = SeriesTeam.objects.filter(series=series)
        existing_ids = set(existing.values_list("team_id", flat=True))
        to_add = new_team_ids - existing_ids
        to_remove = existing_ids - new_team_ids
        scope = request.scope
        with transaction.atomic():
            for team in teams:
                if team.id in to_add:
                    if team.owner_type == "SYSTEM" and not scope.allow_system_data:
                        raise ValidationError("System teams not allowed")
                    SeriesTeam.objects.create(series=series, team=team)
            SeriesTeam.objects.filter(
                series=series,
                team_id__in=to_remove
            ).delete()
        return Response({"status": "teams replaced"})

class SeriesSquadView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, series_team_id):
        series_team = SeriesTeam.objects.get(id=series_team_id)
        validate_series_editable(request, series_team.series)
        squad = SeriesSquad.objects.filter(
            series_team=series_team
        ).select_related("player")
        return Response({
            "series_team_id": series_team.id,
            "is_locked": series_team.series.is_locked,
            "players": [
                {
                    "id": entry.player.id,
                    "name": f"{entry.player.first_name} {entry.player.last_name}",
                    "role": entry.player.role,
                }
                for entry in squad
            ]
        })
    def post(self, request, series_team_id):
        serializer = SeriesSquadBulkInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        series_team = SeriesTeam.objects.get(id=series_team_id)
        validate_series_editable(request, series_team.series)
        player_ids = serializer.validated_data["player_ids"]
        players = Player.objects.filter(id__in=player_ids)
        if players.count() != len(player_ids):
            raise ValidationError("Invalid player id")
        scope = request.scope
        with transaction.atomic():
            for player in players:
                if player.owner_type == "SYSTEM" and not scope.allow_system_data:
                    raise ValidationError("System players not allowed")
                SeriesSquad.objects.get_or_create(
                    series_team=series_team,
                    player=player
                )
        return Response({"status": "players added"})
    def put(self, request, series_team_id):
        serializer = SeriesSquadBulkInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        series_team = SeriesTeam.objects.get(id=series_team_id)
        validate_series_editable(request, series_team.series)
        new_player_ids = set(serializer.validated_data["player_ids"])
        players = Player.objects.filter(id__in=new_player_ids)
        if players.count() != len(new_player_ids):
            raise ValidationError("Invalid player id")
        existing = SeriesSquad.objects.filter(series_team=series_team)
        existing_ids = set(existing.values_list("player_id", flat=True))
        to_add = new_player_ids - existing_ids
        to_remove = existing_ids - new_player_ids
        scope = request.scope
        with transaction.atomic():
            for player in players:
                if player.id in to_add:
                    if player.owner_type == "SYSTEM" and not scope.allow_system_data:
                        raise ValidationError("System players not allowed")
                    SeriesSquad.objects.create(
                        series_team=series_team,
                        player=player
                    )
            SeriesSquad.objects.filter(
                series_team=series_team,
                player_id__in=to_remove
            ).delete()
        return Response({"status": "squad replaced"})