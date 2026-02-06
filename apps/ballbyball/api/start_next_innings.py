"""
API ENTRYPOINT: Start Next Innings

RESPONSIBILITY:
- Creates the next innings (standard/follow-on/super-over)
- Marks it ACTIVE
- Returns state needed for scoring setup
"""
from django.db import transaction
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from matches.models import Match, Innings
from matches.services.innings_transition import prepare_next_innings
from ballbyball.services.validate_match_and_scorer_ownership import (
    validate_match_and_scorer_ownership,
)
from ballbyball.selectors.innings import build_active_innings_read_model
from ballbyball.services.determine_required_scorer_actions import (
    determine_required_scorer_actions,
)
from ballbyball.serializers.ball_delivery_state_response import (
    BallDeliveryStateResponseSerializer,
)
from scoring.models import InningsAggregate
from ballbyball.services.match_context_engine import (
    compute_limited_overs_target,
    compute_fourth_innings_target,
)


class StartNextInningsView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        match = Match.objects.get(id=request.data["match_id"])
        validate_match_and_scorer_ownership(
            user=request.user, match=match
        )

        is_super_over = bool(request.data.get("is_super_over", False))
        enforce_follow_on = bool(request.data.get("enforce_follow_on", False))

        if match.match_type.is_test and is_super_over:
            return Response(
                {"detail": "Super over not allowed for Tests"},
                status=400,
            )

        innings = prepare_next_innings(
            match_id=match.id,
            is_super_over=is_super_over,
            enforce_follow_on=enforce_follow_on,
        )

        innings.state = Innings.State.ACTIVE
        innings.start_time = timezone.now()
        innings.save(update_fields=["state", "start_time"])

        match.state = "IN_PROGRESS"
        match.save(update_fields=["state"])

        aggregate, _ = InningsAggregate.objects.get_or_create(
            innings=innings
        )

        # Set chase targets where applicable
        if not innings.is_super_over:
            if (
                match.match_type.max_innings == 2 and
                innings.innings_number == 2
            ):
                aggregate.is_chasing = True
                aggregate.target_runs = compute_limited_overs_target(
                    match=match
                )
                aggregate.save(
                    update_fields=["is_chasing", "target_runs"]
                )
            elif (
                match.match_type.is_test and
                innings.innings_number == 4
            ):
                aggregate.is_chasing = True
                aggregate.target_runs = compute_fourth_innings_target(
                    match=match,
                    batting_team_id=innings.batting_team_id,
                )
                aggregate.save(
                    update_fields=["is_chasing", "target_runs"]
                )

        state = build_active_innings_read_model(innings=innings)
        actions = determine_required_scorer_actions(state=state)

        events = {
            "wicket": False,
            "over_end": False,
            "innings_end": False,
            "match_end": False,
            "target_state": None,
        }
        next_state = {
            "striker": aggregate.current_striker_id,
            "non_striker": aggregate.current_non_striker_id,
            "bowler": aggregate.current_bowler_id,
        }

        response_serializer = BallDeliveryStateResponseSerializer(
            {
                **state,
                "actions": actions,
                "events": events,
                "next_state": next_state,
            }
        )
        return Response(response_serializer.data)
