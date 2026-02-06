"""
API ENTRYPOINT: Record a Single Ball Delivery

RESPONSIBILITY:
- Accepts ONE delivery payload from frontend
- Coordinates validation, persistence, and response building
- Enforces one-ball-per-request rule

MUST DO:
- Validate request shape
- Delegate ALL cricket logic to services
- Execute inside transaction

MUST NEVER DO:
- Compute runs, overs, strike changes
- Patch aggregates manually
- Handle undo logic
"""

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from matches.models import Match, Innings
from ballbyball.services.validate_match_and_scorer_ownership import (
    validate_match_and_scorer_ownership,
)
from ballbyball.services.persist_ball_and_derived_statistics import (
    persist_ball_and_derived_statistics,
)
from ballbyball.selectors.innings import build_active_innings_read_model
from ballbyball.services.determine_required_scorer_actions import (
    determine_required_scorer_actions,
)
from ballbyball.serializers.ball_delivery_input_payload import (
    BallDeliveryInputPayloadSerializer,
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

from coredata.models import Player

class RecordSingleBallDeliveryView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = BallDeliveryInputPayloadSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        payload = serializer.validated_data

        match = Match.objects.get(id=payload["match_id"])
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

        aggregate = InningsAggregate.objects.get(
            innings=innings
        )
        match_type = innings.match.match_type
        innings_already_ended = detect_innings_end(
            aggregate=aggregate,
            match_type=match_type,
        )
        if innings_already_ended:
            state = build_active_innings_read_model(
                innings=innings
            )
            actions = determine_required_scorer_actions(
                state=state,
                innings_end=True,
                match_end=False,
                ask_follow_on=False,
                confirm_super_over=False,
            )
            return Response(
                {**state, "actions": actions},
                status=409,
            )

        striker = Player.objects.get(id=payload["striker"])
        non_striker = Player.objects.get(id=payload["non_striker"])
        bowler = Player.objects.get(id=payload["bowler"])

        persist_ball_and_derived_statistics(
            user=request.user,
            innings=innings,
            striker=striker,               # object
            non_striker=non_striker,       # object
            bowler=bowler,                 # object
            completed_runs=payload["completed_runs"],
            is_wide=payload["is_wide"],
            is_no_ball=payload["is_no_ball"],
            is_bye=payload["is_bye"],
            is_leg_bye=payload["is_leg_bye"],
            wicket_type=payload.get("wicket_type"),
            dismissed_player_id=payload.get("dismissed_player_id"),
            dismissed_by_id=payload.get("dismissed_by_id"),
            caught_by_id=payload.get("caught_by_id"),
            stumped_by_id=payload.get("stumped_by_id"),
            run_out_fielder_1_id=payload.get("run_out_fielder_1_id"),
            run_out_fielder_2_id=payload.get("run_out_fielder_2_id"),
            analytics=payload.get("analytics"),
            spatial=payload.get("spatial"),
            trajectory=payload.get("trajectory"),
            release=payload.get("release"),
            video=payload.get("video"),
        )

        state = build_active_innings_read_model(
            innings=innings
        )

        aggregate = InningsAggregate.objects.get(innings=innings)
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

        if match_end and innings.match.state != "COMPLETED":
            innings.match.state = "COMPLETED"
            innings.match.save(update_fields=["state"])

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
