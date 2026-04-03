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
    batting_players = PlayingXI.objects.filter(
        match=match,
        team=innings.batting_team
    ).select_related("player").order_by("batting_position")

    bowling_players = PlayingXI.objects.filter(
        match=match,
        team=innings.bowling_team
    ).select_related("player").order_by("-batting_position")  # 🔥 reverse

    return {
        "batters": [
            {
                "id": xi.player.id,
                "first_name": xi.player.first_name,
                "last_name": xi.player.last_name,
                "nick_name": xi.player.nick_name,
                "batting_hand": xi.player.batting_hand,
            }
            for xi in batting_players
        ],
        "bowlers": [
            {
                "id": xi.player.id,
                "first_name": xi.player.first_name,
                "last_name": xi.player.last_name,
                "nick_name": xi.player.nick_name,
                "bowling_hand": xi.player.bowling_hand,
            }
            for xi in bowling_players
        ],
    }