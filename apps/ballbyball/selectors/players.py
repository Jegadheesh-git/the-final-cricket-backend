"""
SELECTOR: Players for Selection

RESPONSIBILITY:
- Fetch valid players for striker/bowler selection

MUST NEVER DO:
- Enforce business rules
"""

from coredata.models import Player
from matches.models import PlayingXI


def get_selectable_players(*, match, innings):
    batting_players = Player.objects.filter(
        id__in=PlayingXI.objects.filter(
            match=match,
            team=innings.batting_team
        ).values_list("player_id", flat=True)
    )

    bowling_players = Player.objects.filter(
        id__in=PlayingXI.objects.filter(
            match=match,
            team=innings.bowling_team
        ).values_list("player_id", flat=True)
    )

    return {
        "batters": list(batting_players.values("id", "first_name")),
        "bowlers": list(bowling_players.values("id", "first_name")),
    }
