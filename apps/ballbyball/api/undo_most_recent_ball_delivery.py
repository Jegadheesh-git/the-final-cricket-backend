"""
API ENTRYPOINT: Undo Most Recent Ball Delivery

RESPONSIBILITY:
- Handles user request to undo last recorded ball
- Delegates deletion and rebuild to service layer

MUST DO:
- Validate match and innings state
- Call undo orchestration service
- Return rebuilt authoritative state

MUST NEVER DO:
- Reverse calculations
- Modify aggregates directly
- Undo more than one ball
"""

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from scoring.models import Ball
from matches.models import Match, Innings
from ballbyball.services.undo_last_recorded_ball import (
    undo_last_recorded_ball,
)
from ballbyball.selectors.innings import build_active_innings_read_model
from ballbyball.services.determine_required_scorer_actions import (
    determine_required_scorer_actions,
)
from ballbyball.serializers.ball_delivery_state_response import (
    BallDeliveryStateResponseSerializer,
)
from scoring.models import InningsAggregate
from ballbyball.services.innings_outcome_engine import (
    detect_innings_end,
    detect_target_state,
    detect_follow_on_required,
    detect_match_end,
)


class UndoMostRecentBallDeliveryView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        match = Match.objects.get(id=request.data["match_id"])
        innings = match.innings.filter(state=Innings.State.ACTIVE).first()

        if match.state == "COMPLETED":
            match.state = "IN_PROGRESS"
            match.save(update_fields=["state"])

        undo_last_recorded_ball(innings=innings)

        state = build_active_innings_read_model(innings=innings)

        aggregate = InningsAggregate.objects.get(
            innings=innings
        )
        match_type = innings.match.match_type
        innings_end = detect_innings_end(
            aggregate=aggregate,
            match_type=match_type,
        )
        target_state = detect_target_state(
            aggregate=aggregate
        )
        ask_follow_on = (
            innings_end and
            detect_follow_on_required(
                match_type=match_type,
                innings_number=innings.innings_number,
            )
        )
        confirm_super_over = (
            innings_end and
            target_state == "TIED" and
            match_type.super_over_allowed
        )
        match_end = (
            innings_end and
            detect_match_end(
                aggregate=aggregate,
                match_type=match_type,
                innings_number=innings.innings_number,
                match=innings.match,
            ) and
            not confirm_super_over
        )

        actions = determine_required_scorer_actions(
            state=state,
            innings_end=innings_end,
            match_end=match_end,
            ask_follow_on=ask_follow_on,
            confirm_super_over=confirm_super_over,
        )

        last_ball = aggregate.last_ball
        balls_per_over = match_type.balls_per_over
        events = {
            "wicket": bool(getattr(last_ball, "wicket", None)) if last_ball else False,
            "over_end": (
                last_ball.is_legal_delivery and
                last_ball.ball_in_over == balls_per_over
            ) if last_ball else False,
            "innings_end": innings_end,
            "match_end": match_end,
            "target_state": target_state,
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
