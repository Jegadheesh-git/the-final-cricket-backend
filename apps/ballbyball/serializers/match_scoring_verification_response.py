"""
SERIALIZER: Match Scoring Verification Response

RESPONSIBILITY:
- Shape response for verify-match endpoint
- Include match metadata and playing XI

MUST NEVER DO:
- Perform validation logic
- Access database directly
"""

from rest_framework import serializers
from matches.models import Match, PlayingXI


class MatchScoringVerificationResponseSerializer(serializers.ModelSerializer):
    playing_xi = serializers.SerializerMethodField()

    class Meta:
        model = Match
        fields = ("id", "team1", "team2", "match_type", "playing_xi")

    def get_playing_xi(self, match):
        xis = PlayingXI.objects.select_related("player").filter(match=match)
        data = {str(match.team1_id): [], str(match.team2_id): []}

        for xi in xis:
            data[str(xi.team_id)].append(
                {
                    "player_id": xi.player_id,
                    "batting_position": xi.batting_position,
                    "is_captain": xi.is_captain,
                    "is_wicket_keeper": xi.is_wicket_keeper,
                }
            )
        return data
