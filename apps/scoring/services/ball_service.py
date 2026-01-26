from uuid import UUID
from django.shortcuts import get_object_or_404
from django.db import transaction

from matches.models import Innings, Match
from scoring.models.ball import Ball
from scoring.models.wicket import BallWicket
from scoring.models.analytics import BallAnalytics
from scoring.models.spatial import BallSpatialOutcome
from scoring.models.trajectory import BallTrajectory
from scoring.models.release import BallReleaseData
from scoring.models.video import BallVideo
from scoring.models.aggregates import InningsAggregate
from scoring.engine.scoring_engine import apply_scoring_engine
from scoring.engine.ball_outcome import build_ball_outcome

@transaction.atomic
def submit_ball(ball_data: dict, user) -> UUID:
    """
    Phase 3 — Persist ball and sub-records.
    NO scoring logic. NO aggregates update.
    """

    innings = get_object_or_404(
        Innings, id=ball_data["innings"]
    )

    match = innings.match

    if match.state != "IN_PROGRESS":
        raise ValueError("Match is not in progress")

    if innings.state != "ACTIVE":
        raise ValueError("Innings is not active")

    aggregate = get_object_or_404(
        InningsAggregate, innings=innings
    )

    # Validate participant consistency
    if (
        ball_data["striker"] != aggregate.current_striker_id or
        ball_data["non_striker"] != aggregate.current_non_striker_id or
        ball_data["bowler"] != aggregate.current_bowler_id
    ):
        raise ValueError("Participants do not match current innings state")

    # Validate ball sequence
    last_ball = (
        Ball.objects
        .filter(innings=innings)
        .order_by("-ball_number")
        .first()
    )

    expected_ball_number = 1 if not last_ball else last_ball.ball_number + 1

    if ball_data["ball_number"] != expected_ball_number:
        raise ValueError("Invalid ball number sequence")

    # Create Ball
    ball = Ball.objects.create(
        user=user,
        match=match,
        innings=innings,
        batting_team=innings.batting_team,
        bowling_team=innings.bowling_team,
        ball_number=ball_data["ball_number"],
        over_number=ball_data["over_number"],
        ball_in_over=ball_data["ball_in_over"],
        striker_id=ball_data["striker"],
        non_striker_id=ball_data["non_striker"],
        bowler_id=ball_data["bowler"],
        runs_off_bat=ball_data["runs"].get("runs_off_bat", 0),
        extra_runs=ball_data["runs"].get("extras", 0),
        bye_runs=ball_data["runs"].get("byes", 0),
        leg_bye_runs=ball_data["runs"].get("leg_byes", 0),
        wide_runs=ball_data["runs"].get("wides", 0),
        no_ball_runs=ball_data["runs"].get("no_balls", 0),
    )

    # Optional sub-records
    if ball_data.get("wicket"):
        BallWicket.objects.create(
            ball=ball,
            **ball_data["wicket"]
        )

    if ball_data.get("analytics"):
        BallAnalytics.objects.create(
            ball=ball,
            **ball_data["analytics"]
        )

    if ball_data.get("spatial"):
        BallSpatialOutcome.objects.create(
            ball=ball,
            **ball_data["spatial"]
        )

    if ball_data.get("trajectory"):
        BallTrajectory.objects.create(
            ball=ball,
            **ball_data["trajectory"]
        )

    if ball_data.get("release"):
        BallReleaseData.objects.create(
            ball=ball,
            **ball_data["release"]
        )

    if ball_data.get("video"):
        BallVideo.objects.create(
            ball=ball,
            **ball_data["video"]
        )

    apply_scoring_engine(ball.id)

    return ball.id
