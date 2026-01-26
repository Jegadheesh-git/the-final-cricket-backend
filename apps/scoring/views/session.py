from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from matches.models import Innings
from scoring.serializers.session import ScoringSessionSerializer
from scoring.serializers.innings_setup import InningsSetupSerializer
from scoring.services.session_service import start_scoring_session
from scoring.services.innings_service import setup_innings
from scoring.services.undo_service import undo_last_ball
from scoring.services.rebuild_service import apply_dls_override

class StartScoringSessionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, match_id):
        data = start_scoring_session(match_id)
        serializer = ScoringSessionSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class InningsSetupAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, innings_id):
        serializer = InningsSetupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        setup_innings(
            innings_id=innings_id,
            striker_id=serializer.validated_data["striker"],
            non_striker_id=serializer.validated_data["non_striker"],
            bowler_id=serializer.validated_data["bowler"],
        )

        return Response(
            {"status": "READY_TO_SCORE"},
            status=status.HTTP_200_OK
        )

class UndoLastBallAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, innings_id):
        undo_last_ball(innings_id)
        return Response({"status": "LAST_BALL_UNDONE"}, status=200)

class ApplyDLSAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, innings_id):
        innings = get_object_or_404(Innings, id=innings_id)

        apply_dls_override(
            innings,
            request.data["revised_target"],
            request.data["revised_overs"],
        )

        return Response({"status": "DLS_APPLIED"}, status=200)
