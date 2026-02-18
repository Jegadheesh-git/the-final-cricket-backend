"""
API ENTRYPOINT: Apply DLS Override

RESPONSIBILITY:
- Apply revised target and/or overs to innings aggregate
"""
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from matches.models import Match, Innings
from scoring.models import InningsAggregate
from ballbyball.services.validate_match_and_scorer_ownership import (
    validate_match_and_scorer_ownership,
)


class ApplyDLSView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        match = Match.objects.get(id=request.data["match_id"])
        validate_match_and_scorer_ownership(
            user=request.user, match=match
        )

        innings_id = request.data.get("innings_id")
        if not innings_id:
            return Response(
                {"detail": "innings_id is required"},
                status=400,
            )

        innings = Innings.objects.get(id=innings_id, match=match)
        aggregate = InningsAggregate.objects.get(innings=innings)

        revised_target = request.data.get("revised_target_runs")
        revised_overs = request.data.get("revised_max_overs")

        if revised_target is None and revised_overs is None:
            return Response(
                {"detail": "revised_target_runs or revised_max_overs required"},
                status=400,
            )

        if revised_target is not None:
            try:
                revised_target = int(revised_target)
            except (TypeError, ValueError):
                return Response({"detail": "revised_target_runs must be a number"}, status=400)
            if revised_target < 0:
                return Response({"detail": "revised_target_runs must be >= 0"}, status=400)
            aggregate.revised_target_runs = revised_target

        if revised_overs is not None:
            try:
                revised_overs = float(revised_overs)
            except (TypeError, ValueError):
                return Response({"detail": "revised_max_overs must be a number"}, status=400)
            if revised_overs <= 0:
                return Response({"detail": "revised_max_overs must be > 0"}, status=400)
            if revised_overs < aggregate.completed_overs:
                return Response(
                    {"detail": "revised_max_overs cannot be less than completed overs"},
                    status=400,
                )
            aggregate.max_overs = revised_overs

        aggregate.save()

        return Response(
            {
                "status": "DLS_APPLIED",
                "match_id": match.id,
                "innings_id": innings.id,
                "revised_target_runs": aggregate.revised_target_runs,
                "revised_max_overs": aggregate.max_overs,
            }
        )
