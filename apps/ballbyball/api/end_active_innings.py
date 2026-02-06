"""
API ENTRYPOINT: End Active Innings

RESPONSIBILITY:
- Ends the currently active innings
- Delegates next-step decision to service layer

MUST DO:
- Validate ownership
- Call innings completion service
- Return next action (new innings or match end)

MUST NEVER DO:
- Decide match result inline
- Create future innings directly
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
from scoring.models import InningsAggregate
from ballbyball.services.innings_outcome_engine import (
    detect_match_end,
)


class EndActiveInningsView(APIView):
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

        innings.state = Innings.State.COMPLETED
        innings.end_time = timezone.now()
        innings.save(update_fields=["state", "end_time"])

        aggregate = InningsAggregate.objects.get(innings=innings)
        match_end = detect_match_end(
            aggregate=aggregate,
            match_type=match.match_type,
            innings_number=innings.innings_number,
            match=match,
        )
        if match_end and match.state != "COMPLETED":
            match.state = "COMPLETED"
            match.save(update_fields=["state"])

        return Response(
            {
                "status": "INNINGS_ENDED",
                "match_id": match.id,
                "innings_id": innings.id,
                "match_ended": match_end,
            }
        )
