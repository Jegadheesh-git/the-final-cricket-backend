import csv
import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from scoring.models import Ball


def value_or_empty(value):
    return "" if value is None else value


class Command(BaseCommand):
    help = (
        "Export one row per ball for a given user id, flattening all ball-related "
        "models into Excel-friendly CSV columns."
    )

    def add_arguments(self, parser):
        parser.add_argument("--user-id", required=True, help="User UUID to export")
        parser.add_argument(
            "--output",
            default="ball_data_export.csv",
            help="Output CSV path. Default: ball_data_export.csv",
        )

    def handle(self, *args, **options):
        user_id = options["user_id"]
        output = Path(options["output"]).expanduser()

        balls = (
            Ball.objects.filter(user_id=user_id)
            .select_related(
                "match",
                "innings",
                "batting_team",
                "bowling_team",
                "striker",
                "non_striker",
                "bowler",
                "umpire_bowler_end",
                "umpire_square_leg",
                "wicket",
                "analytics",
                "spatial_outcome",
                "release_data",
                "video",
                "drs",
            )
            .prefetch_related("trajectory_points", "fieldings")
            .order_by("created_at", "ball_number")
        )

        if not balls.exists():
            raise CommandError(f"No balls found for user_id={user_id}")

        rows = [self.build_row(ball) for ball in balls]
        fieldnames = list(rows[0].keys())

        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

        self.stdout.write(
            self.style.SUCCESS(
                f"Exported {len(rows)} balls for user_id={user_id} to {output}"
            )
        )

    def build_row(self, ball):
        row = {
            "ball_id": ball.id,
            "ball_user_id": value_or_empty(ball.user_id),
            "ball_match_id": value_or_empty(ball.match_id),
            "ball_innings_id": value_or_empty(ball.innings_id),
            "ball_ball_number": value_or_empty(ball.ball_number),
            "ball_over_number": value_or_empty(ball.over_number),
            "ball_ball_in_over": value_or_empty(ball.ball_in_over),
            "ball_is_legal_delivery": value_or_empty(ball.is_legal_delivery),
            "ball_batting_team_id": value_or_empty(ball.batting_team_id),
            "ball_bowling_team_id": value_or_empty(ball.bowling_team_id),
            "ball_striker_id": value_or_empty(ball.striker_id),
            "ball_non_striker_id": value_or_empty(ball.non_striker_id),
            "ball_bowler_id": value_or_empty(ball.bowler_id),
            "ball_umpire_bowler_end_id": value_or_empty(ball.umpire_bowler_end_id),
            "ball_umpire_square_leg_id": value_or_empty(ball.umpire_square_leg_id),
            "ball_striker_hand": value_or_empty(ball.striker_hand),
            "ball_bowler_hand": value_or_empty(ball.bowler_hand),
            "ball_runs_off_bat": value_or_empty(ball.runs_off_bat),
            "ball_completed_runs": value_or_empty(ball.completed_runs),
            "ball_extra_runs": value_or_empty(ball.extra_runs),
            "ball_bye_runs": value_or_empty(ball.bye_runs),
            "ball_leg_bye_runs": value_or_empty(ball.leg_bye_runs),
            "ball_wide_runs": value_or_empty(ball.wide_runs),
            "ball_no_ball_runs": value_or_empty(ball.no_ball_runs),
            "ball_penalty_runs": value_or_empty(ball.penalty_runs),
            "ball_overthrow_runs": value_or_empty(ball.overthrow_runs),
            "ball_is_boundary": value_or_empty(ball.is_boundary),
            "ball_is_short_run": value_or_empty(ball.is_short_run),
            "ball_is_quick_running": value_or_empty(ball.is_quick_running),
            "ball_is_free_hit": value_or_empty(ball.is_free_hit),
            "ball_no_ball_type": value_or_empty(ball.no_ball_type),
            "ball_edit_later": value_or_empty(ball.edit_later),
            "ball_created_at": value_or_empty(ball.created_at),
        }

        self.add_one_to_one(
            row,
            "wicket",
            getattr(ball, "wicket", None),
            [
                "id",
                "wicket_type",
                "dismissed_player_id",
                "dismissed_by_id",
                "caught_by_id",
                "stumped_by_id",
                "run_out_fielder_1_id",
                "run_out_fielder_2_id",
                "decision_given_by_umpire_id",
                "created_at",
            ],
        )
        self.add_one_to_one(
            row,
            "analytics",
            getattr(ball, "analytics", None),
            [
                "id",
                "delivery_type",
                "foot_movement",
                "air_movement",
                "control",
                "shot_connection",
                "bat_subject",
                "stroke",
                "keeper_activity",
                "fielding_activity",
                "batsman_activity",
                "umpire_activity",
                "created_at",
            ],
        )
        self.add_one_to_one(
            row,
            "spatial",
            getattr(ball, "spatial_outcome", None),
            [
                "id",
                "shot_zone_x",
                "shot_zone_y",
                "wagon_wheel_x",
                "wagon_wheel_y",
                "pitch_zone",
                "stump_zone",
                "height_zone",
                "batter_stump_zone",
                "structured_region_id",
                "structured_slice_index",
                "structured_band_index",
                "structured_position",
                "created_at",
            ],
        )
        self.add_one_to_one(
            row,
            "release",
            getattr(ball, "release_data", None),
            [
                "id",
                "bowler_release_x",
                "bowler_release_y",
                "bowler_release_position",
                "wicket_keeper_position",
                "ball_type",
                "is_break",
                "break_type",
                "created_at",
            ],
        )
        self.add_one_to_one(
            row,
            "video",
            getattr(ball, "video", None),
            [
                "id",
                "video_source_id",
                "video_start_ms",
                "video_end_ms",
                "camera_angle",
                "created_at",
            ],
        )
        self.add_one_to_one(
            row,
            "drs",
            getattr(ball, "drs", None),
            [
                "id",
                "is_appealed",
                "review_team_id",
                "review_team_side",
                "on_field_decision",
                "overruled",
                "final_decision",
                "decision_given_by_umpire_id",
                "third_umpire_id",
                "created_at",
            ],
        )

        trajectory_points = list(ball.trajectory_points.all())
        row["trajectory_count"] = len(trajectory_points)
        row["trajectory_points_json"] = json.dumps(
            [
                {
                    "id": str(point.id),
                    "sequence_index": point.sequence_index,
                    "x": point.x,
                    "y": point.y,
                    "z": point.z,
                    "time_ms": point.time_ms,
                    "created_at": point.created_at.isoformat()
                    if point.created_at
                    else None,
                }
                for point in trajectory_points
            ],
            ensure_ascii=True,
        )

        fieldings = list(ball.fieldings.all())
        row["fielding_count"] = len(fieldings)
        row["fieldings_json"] = json.dumps(
            [
                {
                    "id": str(fielding.id),
                    "player_id": str(fielding.player_id) if fielding.player_id else None,
                    "fielder2_id": str(fielding.fielder2_id)
                    if fielding.fielder2_id
                    else None,
                    "action": fielding.action,
                    "fielding_position": fielding.fielding_position,
                    "runs_saved": fielding.runs_saved,
                    "runs_misfielded": fielding.runs_misfielded,
                    "overthrow_runs": fielding.overthrow_runs,
                    "difficulty": fielding.difficulty,
                    "created_at": fielding.created_at.isoformat()
                    if fielding.created_at
                    else None,
                }
                for fielding in fieldings
            ],
            ensure_ascii=True,
        )

        return row

    def add_one_to_one(self, row, prefix, instance, fields):
        if instance is None:
            for field in fields:
                row[f"{prefix}_{field}"] = ""
            return

        for field in fields:
            value = getattr(instance, field, "")
            row[f"{prefix}_{field}"] = value_or_empty(value)
