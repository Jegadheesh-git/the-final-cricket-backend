from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ballbyball.services.validate_match_and_scorer_ownership import (
    validate_match_and_scorer_ownership,
)
from matches.models import Match
from scoring.models import Ball


def serialize_player(player):
    if not player:
        return None
    return {
        "id": str(player.id),
        "first_name": player.first_name,
        "last_name": player.last_name,
        "name": f"{player.first_name} {player.last_name}".strip(),
    }


def serialize_team(team):
    if not team:
        return None
    return {
        "id": str(team.id),
        "name": team.name,
        "short_name": team.short_name,
    }


def serialize_umpire(umpire):
    if not umpire:
        return None
    return {
        "id": str(umpire.id),
        "name": umpire.name,
        "short_name": umpire.short_name,
    }


class MatchBallEntriesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        match = Match.objects.get(id=request.query_params["match_id"])
        validate_match_and_scorer_ownership(user=request.user, match=match)

        balls = (
            Ball.objects.filter(match=match)
            .select_related(
                "innings",
                "batting_team",
                "bowling_team",
                "striker",
                "non_striker",
                "bowler",
                "umpire_bowler_end",
                "umpire_square_leg",
                "wicket",
                "wicket__dismissed_player",
                "wicket__dismissed_by",
                "wicket__caught_by",
                "wicket__stumped_by",
                "wicket__run_out_fielder_1",
                "wicket__run_out_fielder_2",
                "analytics",
                "spatial_outcome",
                "release_data",
                "fielding",
                "fielding__fielder1",
                "fielding__fielder2",
                "drs",
                "drs__review_team",
                "drs__decision_given_by_umpire",
                "drs__third_umpire",
                "video",
            )
            .prefetch_related("trajectory_points")
            .order_by("-innings__innings_number", "-ball_number")[:10]
        )

        entries = []
        for ball in balls:
            display_over_number = max(ball.over_number - 1, 0)
            wicket = getattr(ball, "wicket", None)
            analytics = getattr(ball, "analytics", None)
            spatial = getattr(ball, "spatial_outcome", None)
            release = getattr(ball, "release_data", None)
            fielding = getattr(ball, "fielding", None)
            drs = getattr(ball, "drs", None)
            video = getattr(ball, "video", None)

            entries.append(
                {
                    "id": str(ball.id),
                    "created_at": ball.created_at.isoformat(),
                    "innings": {
                        "id": ball.innings_id,
                        "innings_number": ball.innings.innings_number,
                    },
                    "sequence": {
                        "ball_number": ball.ball_number,
                        "over_number": ball.over_number,
                        "display_over_number": display_over_number,
                        "ball_in_over": ball.ball_in_over,
                        "display": f"{display_over_number}.{ball.ball_in_over}",
                        "is_legal_delivery": ball.is_legal_delivery,
                    },
                    "participants": {
                        "batting_team": serialize_team(ball.batting_team),
                        "bowling_team": serialize_team(ball.bowling_team),
                        "striker": serialize_player(ball.striker),
                        "non_striker": serialize_player(ball.non_striker),
                        "bowler": serialize_player(ball.bowler),
                        "striker_hand": ball.striker_hand,
                        "bowler_hand": ball.bowler_hand,
                        "umpire_bowler_end": serialize_umpire(ball.umpire_bowler_end),
                        "umpire_square_leg": serialize_umpire(ball.umpire_square_leg),
                    },
                    "scoring": {
                        "runs_off_bat": ball.runs_off_bat,
                        "completed_runs": ball.completed_runs,
                        "extra_runs": ball.extra_runs,
                        "bye_runs": ball.bye_runs,
                        "leg_bye_runs": ball.leg_bye_runs,
                        "wide_runs": ball.wide_runs,
                        "no_ball_runs": ball.no_ball_runs,
                        "penalty_runs": ball.penalty_runs,
                        "overthrow_runs": ball.overthrow_runs,
                        "is_boundary": ball.is_boundary,
                        "is_short_run": ball.is_short_run,
                        "is_quick_running": ball.is_quick_running,
                        "is_free_hit": ball.is_free_hit,
                        "no_ball_type": ball.no_ball_type,
                        "edit_later": ball.edit_later,
                    },
                    "wicket": (
                        {
                            "wicket_type": wicket.wicket_type,
                            "dismissed_player": serialize_player(
                                wicket.dismissed_player
                            ),
                            "dismissed_by": serialize_player(wicket.dismissed_by),
                            "caught_by": serialize_player(wicket.caught_by),
                            "stumped_by": serialize_player(wicket.stumped_by),
                            "run_out_fielder_1": serialize_player(
                                wicket.run_out_fielder_1
                            ),
                            "run_out_fielder_2": serialize_player(
                                wicket.run_out_fielder_2
                            ),
                        }
                        if wicket
                        else None
                    ),
                    "analytics": (
                        {
                            "delivery_type": analytics.delivery_type,
                            "foot_movement": analytics.foot_movement,
                            "air_movement": analytics.air_movement,
                            "control": analytics.control,
                            "shot_connection": analytics.shot_connection,
                            "bat_subject": analytics.bat_subject,
                            "stroke": analytics.stroke,
                            "keeper_activity": analytics.keeper_activity,
                            "fielding_activity": analytics.fielding_activity,
                            "batsman_activity": analytics.batsman_activity,
                            "umpire_activity": analytics.umpire_activity,
                        }
                        if analytics
                        else None
                    ),
                    "spatial": (
                        {
                            "shot_zone_x": spatial.shot_zone_x,
                            "shot_zone_y": spatial.shot_zone_y,
                            "wagon_wheel_x": spatial.wagon_wheel_x,
                            "wagon_wheel_y": spatial.wagon_wheel_y,
                            "pitch_zone": spatial.pitch_zone,
                            "stump_zone": spatial.stump_zone,
                            "height_zone": spatial.height_zone,
                            "batter_stump_zone": spatial.batter_stump_zone,
                            "structured_region_id": spatial.structured_region_id,
                            "structured_slice_index": spatial.structured_slice_index,
                            "structured_band_index": spatial.structured_band_index,
                            "structured_position": spatial.structured_position,
                        }
                        if spatial
                        else None
                    ),
                    "release": (
                        {
                            "bowler_release_x": release.bowler_release_x,
                            "bowler_release_y": release.bowler_release_y,
                            "bowler_release_position": release.bowler_release_position,
                            "wicket_keeper_position": release.wicket_keeper_position,
                            "ball_type": release.ball_type,
                            "is_break": release.is_break,
                            "break_type": release.break_type,
                        }
                        if release
                        else None
                    ),
                    "fielding": (
                        {
                            "fielder1": serialize_player(fielding.fielder1),
                            "fielder2": serialize_player(fielding.fielder2),
                            "action": fielding.action,
                            "fielding_position": fielding.fielding_position,
                            "runs_saved": fielding.runs_saved,
                            "runs_misfielded": fielding.runs_misfielded,
                            "overthrow_runs": fielding.overthrow_runs,
                            "difficulty": fielding.difficulty,
                        }
                        if fielding
                        else None
                    ),
                    "drs": (
                        {
                            "is_appealed": drs.is_appealed,
                            "review_team": serialize_team(drs.review_team),
                            "review_team_side": drs.review_team_side,
                            "on_field_decision": drs.on_field_decision,
                            "overruled": drs.overruled,
                            "final_decision": drs.final_decision,
                            "decision_given_by_umpire": serialize_umpire(
                                drs.decision_given_by_umpire
                            ),
                            "third_umpire": serialize_umpire(drs.third_umpire),
                        }
                        if drs
                        else None
                    ),
                    "video": (
                        {
                            "video_source_id": video.video_source_id,
                            "video_start_ms": video.video_start_ms,
                            "video_end_ms": video.video_end_ms,
                            "camera_angle": video.camera_angle,
                        }
                        if video
                        else None
                    ),
                    "trajectory": [
                        {
                            "sequence_index": point.sequence_index,
                            "x": point.x,
                            "y": point.y,
                            "z": point.z,
                            "time_ms": point.time_ms,
                        }
                        for point in ball.trajectory_points.all()
                    ],
                }
            )

        return Response(
            {
                "match_id": str(match.id),
                "entry_count": len(entries),
                "entries": entries,
            }
        )
