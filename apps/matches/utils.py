from rest_framework.exceptions import ValidationError, PermissionDenied
from competitions.models import CompetitionSquad, SeriesSquad
from matches.models import PlayingXI, Toss, Innings
import uuid

def ensure_owner(scope, obj):
    check_id = scope.owner_id
    if isinstance(check_id, int) and isinstance(obj.owner_id, uuid.UUID):
        try:
            check_id = uuid.UUID(int=check_id)
        except ValueError:
            pass
            
    if obj.owner_type != scope.owner_type or obj.owner_id != check_id:
        raise PermissionDenied("Not allowed")
def ensure_state(match, allowed_states):
    if match.state not in allowed_states:
        raise ValidationError(
            f"Invalid state transition from {match.state}"
        )

def ensure_match_ready(match):
    if match.state != "READY":
        raise ValidationError(
            "Playing XI can be set only when match is READY"
        )
def ensure_xi_not_started(match):
    if match.state in ("IN_PROGRESS", "COMPLETED"):
        raise ValidationError("Match already started")
def ensure_players_from_squad(match, team_id, player_ids):
    if match.competition:
        qs = CompetitionSquad.objects.filter(
            competition_team__competition=match.competition,
            competition_team__team_id=team_id,
            player_id__in=player_ids
        )
    else:
        qs = SeriesSquad.objects.filter(
            series_team__series=match.series,
            series_team__team_id=team_id,
            player_id__in=player_ids
        )
    if qs.count() != len(player_ids):
        raise ValidationError("All players must belong to squad")

def playing_xi_count(match, team_id):
    return PlayingXI.objects.filter(
        match=match,
        team_id=team_id
    ).count()

def ensure_toss_not_exists(match):
    if Toss.objects.filter(match=match).exists():
        raise ValidationError("Toss already exists")

def ensure_team_in_match(match, team_id):
    if team_id not in [match.team1_id, match.team2_id]:
        raise ValidationError("Invalid team for this match")

def ensure_toss_exists(match):
    if not hasattr(match, "toss"):
        raise ValidationError("Toss must be completed")
def ensure_no_active_innings(match):
    if Innings.objects.filter(
        match=match
    ).exclude(state__in=["COMPLETED", "ABANDONED"]).exists():
        raise ValidationError("Previous innings not completed")
        
def next_innings_number(match):
    return Innings.objects.filter(match=match).count() + 1







