import hashlib
import json
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404


from backend.core.viewsets import OwnedModelViewSet
from competitions.models import Competition, Series
from .models import Match, PlayingXI, Toss, Innings
from .serializers import MatchCreateSerializer, PlayingXIInputSerializer, TossCreateSerializer, InningsCreateSerializer, MatchDetailSerializer
from .utils import (
    ensure_owner,
    ensure_match_ready,
    ensure_xi_not_started,
    ensure_players_from_squad,
    ensure_toss_not_exists,
    ensure_team_in_match,
    ensure_toss_exists,
    ensure_no_active_innings,
    next_innings_number,
)

from matches.services.innings_transition import (
    end_innings,
    prepare_next_innings,
    end_match,
)

class MatchViewSet(OwnedModelViewSet):
    
    serializer_class = MatchCreateSerializer
    queryset = Match.objects.all()
   
    """
    def perform_create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        match = serializer.save(state="DRAFT",owner_type=scope.owner_type, owner_id=scope.owner_id, is_locked=False)

        scope = request.scope

        # Ownership validation
        if match.competition:
            ensure_owner(scope, match.competition)
        else:
            ensure_owner(scope, match.series)

        return Response(
            {
                "id": match.id,
                "state": match.state
            },
            status=status.HTTP_201_CREATED
        )
        """
    
class PrepareOfflineMatchView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, match_id):
        match = Match.objects.select_related(
            "competition", "series", "match_type"
        ).get(id=match_id)
        scope = request.scope
        # Ownership
        if match.competition:
            ensure_owner(scope, match.competition)
        else:
            ensure_owner(scope, match.series)
        # State + mode validation
        if match.match_mode != "OFFLINE":
            raise ValidationError("Match is not offline")
        if match.state != "DRAFT":
            raise ValidationError("Match already prepared")
        # TODO later:
        # - validate squads exist for both teams
        # Generate deterministic snapshot hash
        snapshot_payload = {
            "match_id": str(match.id),
            "match_type": match.match_type.code,
            "team1": str(match.team1.id),
            "team2": str(match.team2.id),
            "mode": match.match_mode,
        }
        raw = json.dumps(snapshot_payload, sort_keys=True).encode()
        snapshot_hash = hashlib.sha256(raw).hexdigest()
        match.offline_snapshot_hash = snapshot_hash
        match.state = "READY"
        match.save(update_fields=["offline_snapshot_hash", "state"])
        # Lock parent
        if match.competition:
            match.competition.is_locked = True
            match.competition.save(update_fields=["is_locked"])
        else:
            match.series.is_locked = True
            match.series.save(update_fields=["is_locked"])
        return Response({
            "status": "offline prepared",
            "snapshot_hash": snapshot_hash,
            "state": match.state,
        })

class ConfirmOnlineMatchView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, match_id):
        match = Match.objects.select_related(
            "competition", "series"
        ).get(id=match_id)
        scope = request.scope
        if match.match_mode != "ONLINE":
            raise ValidationError("Match is not online")
        if match.state != "DRAFT":
            raise ValidationError("Match already confirmed")
        # Ownership
        if match.competition:
            ensure_owner(scope, match.competition)
            match.competition.is_locked = True
            match.competition.save(update_fields=["is_locked"])
        else:
            ensure_owner(scope, match.series)
            match.series.is_locked = True
            match.series.save(update_fields=["is_locked"])
        match.state = "READY"
        match.save(update_fields=["state"])
        return Response({
            "status": "online confirmed",
            "state": match.state
        })

class StartMatchView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, match_id):
        match = Match.objects.get(id=match_id)
        if match.state != "READY":
            raise ValidationError("Match not ready to start")
        match.state = "IN_PROGRESS"
        match.save(update_fields=["state"])
        return Response({
            "status": "match started",
            "state": match.state
        })

class CompleteMatchView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, match_id):
        match = Match.objects.get(id=match_id)
        if match.state != "IN_PROGRESS":
            raise ValidationError("Match not in progress")
        match.state = "COMPLETED"
        match.save(update_fields=["state"])
        return Response({
            "status": "match completed",
            "state": match.state
        })

class OfflineSyncView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, match_id):
        match = Match.objects.get(id=match_id)
        if match.match_mode != "OFFLINE":
            raise ValidationError("Not an offline match")
        if match.state != "READY":
            raise ValidationError("Match not ready for sync")
        incoming_hash = request.data.get("snapshot_hash")
        if incoming_hash != match.offline_snapshot_hash:
            raise ValidationError("Snapshot mismatch")
        # TODO later:
        # - save toss
        # - save XI
        # - save balls
        match.state = "COMPLETED"
        match.save(update_fields=["state"])
        return Response({
            "status": "offline sync successful",
            "state": match.state
        })


class PlayingXIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, match_id):
        match = Match.objects.get(id=match_id)
        data = {}
        for team_id in [match.team1_id, match.team2_id]:
            xis = PlayingXI.objects.filter(
                match=match,
                team_id=team_id
            ).select_related("player")
            data[str(team_id)] = [
                {
                    "player_id": xi.player_id,
                    "batting_position": xi.batting_position,
                    "is_captain": xi.is_captain,
                    "is_wicket_keeper": xi.is_wicket_keeper,
                }
                for xi in xis
            ]
        return Response({
            "match_id": match.id,
            "state": match.state,
            "playing_xi": data,
        })

    def put(self, request, match_id):
        match = Match.objects.get(id=match_id)
        ensure_match_ready(match)
        ensure_xi_not_started(match)
        if match.match_mode == "OFFLINE":
            raise ValidationError(
                "Playing XI for offline matches must be set offline"
            )
        serializer = PlayingXIInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        team_id = serializer.validated_data["team_id"]
        players = serializer.validated_data["players"]
        if team_id not in [match.team1_id, match.team2_id]:
            raise ValidationError("Invalid team for this match")
        player_ids = [p["player_id"] for p in players]
        #ensure_players_from_squad(match, team_id, player_ids)
        with transaction.atomic():
            PlayingXI.objects.filter(
                match=match,
                team_id=team_id
            ).delete()
            for p in players:
                PlayingXI.objects.create(
                    match=match,
                    team_id=team_id,
                    player_id=p["player_id"],
                    batting_position=p["batting_position"],
                    is_captain=p.get("is_captain", False),
                    is_wicket_keeper=p.get("is_wicket_keeper", False),
                )
        return Response(
            {"status": "playing xi set"},
            status=status.HTTP_200_OK
        )
    
class MatchDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, match_id):
        match = get_object_or_404(
            Match.objects.select_related(
                "competition",
                "series",
                "team1",
                "team2",
            ),
            id=match_id
        )
        serializer = MatchDetailSerializer(match)
        return Response(serializer.data)

class TossView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, match_id):
        match = Match.objects.get(id=match_id)
        toss = getattr(match, "toss", None)
        if not toss:
            return Response({
                "match_id": match.id,
                "toss": None
            })
        return Response({
            "match_id": match.id,
            "toss": {
                "won_by": toss.won_by_id,
                "decision": toss.decision,
            }
        })
    def post(self, request, match_id):
        match = Match.objects.get(id=match_id)
        if match.match_mode == "OFFLINE":
            raise ValidationError(
                "Toss for offline matches must be done offline"
            )
        if match.state != "READY":
            raise ValidationError(
                "Toss can be done only when match is READY"
            )
        ensure_toss_not_exists(match)
        serializer = TossCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        won_by = serializer.validated_data["won_by"]
        decision = serializer.validated_data["decision"]
        ensure_team_in_match(match, won_by)
        Toss.objects.create(
            match=match,
            won_by_id=won_by,
            decision=decision
        )
        return Response(
            {"status": "toss completed"},
            status=status.HTTP_201_CREATED
        )

class InningsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, match_id):
        match = Match.objects.get(id=match_id)
        innings = Innings.objects.filter(match=match)
        return Response({
            "match_id": match.id,
            "innings": [
                {
                    "innings_number": i.innings_number,
                    "batting_team": i.batting_team_id,
                    "bowling_team": i.bowling_team_id,
                    "runs": i.runs,
                    "wickets": i.wickets,
                    "overs": float(i.overs),
                    "is_completed": i.is_completed,
                }
                for i in innings
            ]
        })
    def post(self, request, match_id):
        match = Match.objects.get(id=match_id)
        if match.match_mode == "OFFLINE":
            raise ValidationError(
                "Innings for offline matches must be created offline"
            )
        if match.state != "READY":
            raise ValidationError(
                "Match must be READY to start innings"
            )
        ensure_toss_exists(match)
        ensure_no_active_innings(match)
        serializer = InningsCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        batting_team = serializer.validated_data["batting_team"]
        ensure_team_in_match(match, batting_team)
        bowling_team = (
            match.team2_id
            if batting_team == match.team1_id
            else match.team1_id
        )
        innings = Innings.objects.create(
            match=match,
            batting_team_id=batting_team,
            bowling_team_id=bowling_team,
            innings_number=next_innings_number(match),
        )
        # First innings starts match
        if match.state == "READY":
            match.state = "IN_PROGRESS"
            match.save(update_fields=["state"])
        return Response(
            {
                "status": "innings started",
                "innings_number": innings.innings_number,
            },
            status=status.HTTP_201_CREATED
        )
    def patch(self, request, match_id, innings_number):
        match = Match.objects.get(id=match_id)
        if match.match_mode == "OFFLINE":
            raise ValidationError(
                "Offline innings completion happens during sync"
            )
        innings = Innings.objects.get(
            match=match,
            innings_number=innings_number
        )
        if innings.is_completed:
            raise ValidationError("Innings already completed")
        innings.is_completed = True
        innings.end_time = timezone.now()
        innings.save(update_fields=["is_completed", "end_time"])
        return Response({"status": "innings completed"})

class EndInningsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, innings_id):
        end_innings(innings_id)
        return Response({"status": "INNINGS_ENDED"}, status=200)

class PrepareNextInningsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, match_id):
        innings = prepare_next_innings(match_id)
        return Response(
            {
                "status": "NEXT_INNINGS_CREATED",
                "innings_id": innings.id,
            },
            status=201,
        )

class EndMatchAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, match_id):
        end_match(match_id)
        return Response({"status": "MATCH_ENDED"}, status=200)

class MatchStateUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, match_id):
        new_state = request.data.get("state")

        if not new_state:
            return Response(
                {"detail": "state is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        allowed_states = [choice[0] for choice in Match.STATE_CHOICES]
        if new_state not in allowed_states:
            return Response(
                {
                    "detail": "Invalid state",
                    "allowed_states": allowed_states
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        match = get_object_or_404(Match, id=match_id)

        match.state = new_state
        match.save(update_fields=["state"])

        return Response(
            {
                "id": match.id,
                "state": match.state
            },
            status=status.HTTP_200_OK
        )