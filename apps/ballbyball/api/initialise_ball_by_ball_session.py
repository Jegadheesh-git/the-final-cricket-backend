"""
API ENTRYPOINT: Initialise Ball-by-Ball Session

RESPONSIBILITY:
- Starts or resumes a scoring session for a match
- Called only after match verification succeeds
- Delegates innings creation to service layer

MUST DO:
- Validate ownership
- Call session start service
- Return identifiers needed by frontend

MUST NEVER DO:
- Save balls
- Compute aggregates
- Contain cricket rules
"""

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from matches.models import Match, Innings
from ballbyball.services.validate_match_and_scorer_ownership import (
    validate_match_and_scorer_ownership,
)
from ballbyball.services.start_or_resume_innings_session import (
    start_or_resume_innings_session,
)
from ballbyball.services.determine_required_scorer_actions import (
    determine_required_scorer_actions,
)
from ballbyball.selectors.innings import build_active_innings_read_model
from scoring.models import InningsAggregate
from ballbyball.services.innings_outcome_engine import (
    detect_innings_end,
    detect_target_state,
    detect_follow_on_required,
    detect_match_end,
)


class InitialiseBallByBallSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        match = Match.objects.get(id=request.data["match_id"])
        validate_match_and_scorer_ownership(user=request.user, match=match)
        innings = start_or_resume_innings_session(match=match)
        competition_label = None
        if match.competition:
            competition_label = match.competition.name
        elif match.series:
            competition_label = match.series.name
        date_label = match.match_date.isoformat() if match.match_date else None
        match_title = (
            f"{match.team1.name} vs {match.team2.name}"
            f"{' (' + competition_label + ')' if competition_label else ''}"
            f"{' on ' + date_label if date_label else ''}"
        )
        return Response(
            {
                "match_id": match.id,
                "innings_id": innings.id,
                "match_ended": match.state == "COMPLETED",
                "match_title": match_title,
                "batting_team_name": innings.batting_team.name,
                "bowling_team_name": innings.bowling_team.name,
                "current_innings_number": innings.innings_number,
            }
        )

    def get(self, request):
        match = Match.objects.get(id=request.query_params["match_id"])
        validate_match_and_scorer_ownership(user=request.user, match=match)

        innings = match.innings.filter(state=Innings.State.ACTIVE).first()
        if not innings:
            return Response({"detail": "No active innings"}, status=409)

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

        competition_label = None
        if match.competition:
            competition_label = match.competition.name
        elif match.series:
            competition_label = match.series.name
        date_label = match.match_date.isoformat() if match.match_date else None
        match_title = (
            f"{match.team1.name} vs {match.team2.name}"
            f"{' (' + competition_label + ')' if competition_label else ''}"
            f"{' on ' + date_label if date_label else ''}"
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

        return Response(
            {
                **state,
                "actions": actions,
                "events": events,
                "next_state": next_state,
                "match_ended": match.state == "COMPLETED",
                "match_title": match_title,
                "batting_team_name": innings.batting_team.name,
                "bowling_team_name": innings.bowling_team.name,
                "current_innings_number": innings.innings_number,
            }
        )
