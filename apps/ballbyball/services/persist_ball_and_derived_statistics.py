"""
SERVICE: Persist Ball and Derived Statistics

RESPONSIBILITY:
- Create Ball record
- Create BallWicket if applicable
- Update InningsAggregate
- Update BatterStats and BowlerStats

MUST DO:
- Run inside transaction
- Be deterministic

MUST NEVER DO:
- Decide UI actions
- Handle undo
"""
from django.db import transaction
from scoring.models import (
    Ball,
    BatterStats,
    BowlerStats,
    InningsAggregate,
    BallWicket,
    BallAnalytics,
    BallSpatialOutcome,
    BallTrajectory,
    BallReleaseData,
    BallVideo,
)
from ballbyball.services.calculate_next_ball_sequence_numbers import (
    calculate_next_ball_sequence_numbers,
)
from ballbyball.services.ball_outcome_engine import (
    derive_next_state,
)
from ballbyball.services.innings_outcome_engine import (
    detect_target_state,
)
import re


@transaction.atomic
def persist_ball_and_derived_statistics(
    *,
    user,
    innings,
    striker,
    non_striker,
    bowler,
    completed_runs,
    is_wide,
    is_no_ball,
    is_bye,
    is_leg_bye,
    dismissed_player_id=None,
    wicket_type=None,
    dismissed_by_id=None,
    caught_by_id=None,
    stumped_by_id=None,
    run_out_fielder_1_id=None,
    run_out_fielder_2_id=None,
    analytics=None,
    spatial=None,
    trajectory=None,
    release=None,
    video=None,

):
    def to_snake(value):
        return re.sub(r"(?<!^)([A-Z])", r"_\\1", value).lower()

    def normalize_keys(payload):
        if not payload:
            return payload
        return {to_snake(k): v for k, v in payload.items()}

    def normalize_list(payload_list):
        if not payload_list:
            return payload_list
        return [normalize_keys(item) for item in payload_list]
    if striker == non_striker:
        raise ValueError("Striker and non-striker cannot be same")

    if bowler == striker or bowler == non_striker:
        raise ValueError("Bowler cannot be a batter")

    if is_bye and is_leg_bye:
        raise ValueError("Ball cannot be both bye and leg-bye")

    if is_wide and (is_bye or is_leg_bye):
        raise ValueError("Wide cannot be a bye or leg-bye")

    if wicket_type and not dismissed_player_id:
        raise ValueError("dismissed_player_id required for wicket")

    aggregate = InningsAggregate.objects.select_for_update().get(
        innings=innings
    )

    _, over_number, ball_in_over = (
        calculate_next_ball_sequence_numbers(
            aggregate=aggregate,
            balls_per_over=innings.match.match_type.balls_per_over,
        )
    )

    last_ball = aggregate.last_ball
    ball_number = 1 if not last_ball else last_ball.ball_number + 1

    # Legality
    is_legal_delivery = not (is_wide or is_no_ball)

    # Classify completed runs
    runs_off_bat = 0
    bye_runs = 0
    leg_bye_runs = 0

    if completed_runs > 0:
        if is_bye:
            bye_runs = completed_runs
        elif is_leg_bye:
            leg_bye_runs = completed_runs
        else:
            runs_off_bat = completed_runs

    # Extras breakdown
    wide_runs = 0
    no_ball_runs = 0
    penalty_runs = 0

    if is_wide:
        wide_runs = 1 + completed_runs
        penalty_runs += 1

    if is_no_ball:
        no_ball_runs = 1
        penalty_runs += 1

    extra_runs = wide_runs + no_ball_runs + bye_runs + leg_bye_runs
    total_runs = runs_off_bat + extra_runs


    ball = Ball.objects.create(
        user=user,
        match=innings.match,
        innings=innings,
        ball_number=ball_number,
        over_number=over_number,
        ball_in_over=ball_in_over,
        is_legal_delivery=is_legal_delivery,
        batting_team=innings.batting_team,
        bowling_team=innings.bowling_team,
        striker=striker,
        non_striker=non_striker,
        bowler=bowler,
        runs_off_bat=runs_off_bat,
        completed_runs=completed_runs,
        extra_runs=extra_runs,
        bye_runs=bye_runs,
        leg_bye_runs=leg_bye_runs,
        wide_runs=wide_runs,
        no_ball_runs=no_ball_runs,
        penalty_runs=penalty_runs,
        is_boundary=completed_runs in (4, 6),
    )

    if wicket_type and dismissed_player_id:
        if wicket_type != "RUN_OUT" and dismissed_player_id != striker.id:
            raise ValueError("Only run-out can dismiss non-striker")
        BallWicket.objects.create(
            ball=ball,
            wicket_type=wicket_type,
            dismissed_player_id=dismissed_player_id,
            dismissed_by_id=dismissed_by_id,
            caught_by_id=caught_by_id,
            stumped_by_id=stumped_by_id,
            run_out_fielder_1_id=run_out_fielder_1_id,
            run_out_fielder_2_id=run_out_fielder_2_id,
        )

    if analytics:
        BallAnalytics.objects.create(
            ball=ball,
            **normalize_keys(analytics),
        )

    if spatial:
        BallSpatialOutcome.objects.create(
            ball=ball,
            **normalize_keys(spatial),
        )

    if release:
        BallReleaseData.objects.create(
            ball=ball,
            **normalize_keys(release),
        )

    if video:
        BallVideo.objects.create(
            ball=ball,
            **normalize_keys(video),
        )

    if trajectory:
        for point in normalize_list(trajectory):
            BallTrajectory.objects.create(
                ball=ball,
                **point,
            )

    outcome = derive_next_state(
        striker_id=striker.id,
        non_striker_id=non_striker.id,
        bowler_id=bowler.id,
        ball=ball,
        balls_per_over=innings.match.match_type.balls_per_over,
        dismissed_player_id=dismissed_player_id,
    )

    # Aggregate update
    aggregate.runs += total_runs
    aggregate.extras += extra_runs
    if wicket_type and dismissed_player_id:
        aggregate.wickets += 1

    if is_legal_delivery:
        aggregate.legal_balls += 1
        if ball_in_over == innings.match.match_type.balls_per_over:
            aggregate.completed_overs += 1

    aggregate.current_striker_id = outcome["next_striker"]
    aggregate.current_non_striker_id = outcome["next_non_striker"]
    aggregate.current_bowler_id = outcome["next_bowler"]
    aggregate.last_ball = ball
    aggregate.save()

    # Batter stats
    batter, _ = BatterStats.objects.get_or_create(
        innings=innings,
        player=striker,
    )
    batter.runs += runs_off_bat
    if is_legal_delivery:
        batter.balls += 1
    if runs_off_bat == 4:
        batter.fours += 1
    elif runs_off_bat == 6:
        batter.sixes += 1
    if wicket_type and dismissed_player_id == striker.id:
        batter.is_out = True
        batter.dismissal_ball = ball
    batter.save()

    # Bowler stats
    bowler_stats, _ = BowlerStats.objects.get_or_create(
        innings=innings,
        player=bowler,
    )
    bowler_stats.runs_conceded += runs_off_bat + wide_runs + no_ball_runs
    if is_wide:
        bowler_stats.wides += 1
    if is_no_ball:
        bowler_stats.no_balls += 1
    if is_legal_delivery:
        bowler_stats.balls += 1
    if wicket_type in {"BOWLED", "LBW", "CAUGHT", "STUMPED", "HIT_WICKET"}:
        credited_to_bowler = (
            dismissed_by_id is None or dismissed_by_id == bowler.id
        )
        if credited_to_bowler:
            bowler_stats.wickets += 1
    bowler_stats.save()

    target_state = detect_target_state(aggregate=aggregate)
    aggregate.target_achieved = target_state == "WON"
    aggregate.save(update_fields=["target_achieved"])

    return ball
