"""
API ENTRYPOINT: End Match

RESPONSIBILITY:
- Ends the match explicitly
"""
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from matches.models import Match
from matches.services.innings_transition import end_match
from ballbyball.services.validate_match_and_scorer_ownership import (
    validate_match_and_scorer_ownership,
)


class EndMatchView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        match = Match.objects.get(id=request.data["match_id"])
        validate_match_and_scorer_ownership(
            user=request.user, match=match
        )

        end_match(match.id)

        return Response(
            {
                "status": "MATCH_ENDED",
                "match_id": match.id,
            }
        )
