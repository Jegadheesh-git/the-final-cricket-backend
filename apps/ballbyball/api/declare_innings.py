"""
API ENTRYPOINT: Declare Innings (Test)

RESPONSIBILITY:
- Allows batting side to declare an innings
"""
from django.utils import timezone
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from matches.models import Match, Innings
from ballbyball.services.validate_match_and_scorer_ownership import (
    validate_match_and_scorer_ownership,
)


class DeclareInningsView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        match = Match.objects.get(id=request.data["match_id"])
        validate_match_and_scorer_ownership(
            user=request.user, match=match
        )

        innings = match.innings.filter(
            state=Innings.State.ACTIVE
        ).first()
        if not innings:
            return Response(
                {"detail": "No active innings"},
                status=409,
            )

        if not match.match_type.is_test:
            return Response(
                {"detail": "Declarations only allowed in Tests"},
                status=400,
            )

        innings.state = Innings.State.COMPLETED
        innings.end_time = timezone.now()
        innings.save(update_fields=["state", "end_time"])

        return Response(
            {
                "status": "INNINGS_DECLARED",
                "match_id": match.id,
                "innings_id": innings.id,
            }
        )
