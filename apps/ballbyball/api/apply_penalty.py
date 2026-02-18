"""
API ENTRYPOINT: Apply Penalty Runs
"""
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from matches.models import Match, Innings
from ballbyball.services.validate_match_and_scorer_ownership import (
    validate_match_and_scorer_ownership,
)
from scoring.models import InningsAggregate
from scoring.models import InningsPenalty


class ApplyPenaltyView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        match = Match.objects.get(id=request.data["match_id"])
        validate_match_and_scorer_ownership(
            user=request.user, match=match
        )

        innings_id = request.data.get("innings_id")
        if not innings_id:
            return Response({"detail": "innings_id is required"}, status=400)

        innings = Innings.objects.get(id=innings_id, match=match)

        runs = int(request.data.get("runs", 0))
        if runs <= 0:
            return Response({"detail": "runs must be > 0"}, status=400)

        awarded_to = request.data.get("awarded_to")
        if awarded_to not in ("BATTING", "BOWLING"):
            return Response({"detail": "awarded_to must be BATTING or BOWLING"}, status=400)

        reason = request.data.get("reason") or ""
        reason_other = request.data.get("reason_other") or ""

        if awarded_to == "BATTING":
            awarded_team = innings.batting_team
            awarded_innings = innings
        else:
            awarded_team = innings.bowling_team
            awarded_innings = (
                Innings.objects.filter(
                    match=match,
                    batting_team=awarded_team,
                    is_super_over=False
                )
                .order_by("innings_number")
                .first()
            )
            if not awarded_innings:
                # Create future innings (OPEN) to hold penalty runs
                next_number = Innings.objects.filter(match=match).count() + 1
                awarded_innings = Innings.objects.create(
                    match=match,
                    innings_number=next_number,
                    batting_team=awarded_team,
                    bowling_team=innings.batting_team,
                    state=Innings.State.OPEN,
                    is_super_over=False,
                )

        aggregate, _ = InningsAggregate.objects.get_or_create(
            innings=awarded_innings
        )
        aggregate.runs += runs
        aggregate.extras += runs
        aggregate.extra_penalty_runs += runs

        aggregate.save()

        penalty = InningsPenalty.objects.create(
            match=match,
            innings=innings,
            awarded_to_innings=awarded_innings,
            awarded_team=awarded_team,
            awarded_to=awarded_to,
            reason=reason,
            reason_other=reason_other,
            runs=runs,
        )

        return Response(
            {
                "status": "PENALTY_APPLIED",
                "penalty_id": penalty.id,
                "awarded_to_innings_id": awarded_innings.id,
                "awarded_team_id": awarded_team.id,
            }
        )
