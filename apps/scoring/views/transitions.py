from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from matches.models import Match, Innings
from matches.services.innings_transition import end_innings, prepare_next_innings, end_match
from scoring.serializers.session import ScoringSessionSerializer

class EndInningsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, innings_id):
        try:
            end_innings(innings_id)
            return Response({"status": "INNINGS_ENDED"}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class NextInningsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, match_id):
        try:
            transition_type = request.data.get("type", "STANDARD")
            
            is_super_over = (transition_type == "SUPER_OVER")
            enforce_follow_on = (transition_type == "FOLLOW_ON")
            
            new_innings = prepare_next_innings(
                match_id, 
                is_super_over=is_super_over,
                enforce_follow_on=enforce_follow_on
            )
            
            return Response({
                "status": "NEXT_INNINGS_CREATED",
                "innings_id": new_innings.id,
                "innings_number": new_innings.innings_number,
                "is_super_over": new_innings.is_super_over
            }, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class EndMatchAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, match_id):
        end_match(match_id)
        return Response({"status": "MATCH_COMPLETED"}, status=status.HTTP_200_OK)
