"""
API ENTRYPOINT: Verify Match Readiness for Ball-by-Ball Scoring

RESPONSIBILITY:
- Acts as the HTTP entry point when a user clicks "Start Ball Collection"
- Accepts match_id and authenticated user
- Delegates ALL validation to service layer
- Returns a read-only response indicating whether scoring is allowed

MUST DO:
- Call ownership validation
- Call match readiness checks
- Return structured response

MUST NEVER DO:
- Create innings
- Modify match state
- Contain cricket logic
- Access ORM directly (beyond fetching match reference)
"""
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from matches.models import Match, PlayingXI
from ballbyball.services.validate_match_and_scorer_ownership import (
    validate_match_and_scorer_ownership,
)
from ballbyball.serializers.match_scoring_verification_response import (
    MatchScoringVerificationResponseSerializer,
)


class VerifyMatchReadyForBallByBallScoringView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        match_id = request.data.get("match_id")
        if not match_id:
            return Response({"allowed": False, "reason": "match_id required"}, status=400)

        try:
            match = Match.objects.get(id=match_id)
        except Match.DoesNotExist:
            return Response({"allowed": False, "reason": "Match not found"}, status=404)

        validate_match_and_scorer_ownership(user=request.user, match=match)

        if match.match_mode != "ONLINE":
            return Response({"allowed": False, "reason": "Match not ONLINE"})

        if match.state not in ("READY", "IN_PROGRESS"):
            return Response({"allowed": False, "reason": "Match not ready"})

        if not hasattr(match, "toss"):
            return Response({"allowed": False, "reason": "Toss not completed"})

        teams = {match.team1_id, match.team2_id}
        xi_teams = set(
            PlayingXI.objects.filter(match=match)
            .values_list("team_id", flat=True)
            .distinct()
        )

        if teams != xi_teams:
            return Response({"allowed": False, "reason": "Playing XI incomplete"})

        serializer = MatchScoringVerificationResponseSerializer(match)

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

        team1_players = PlayingXI.objects.filter(
            match=match,
            team=match.team1,
        ).select_related("player")
        team2_players = PlayingXI.objects.filter(
            match=match,
            team=match.team2,
        ).select_related("player")

        return Response(
            {
                "allowed": True,
                **serializer.data,
                "team1_name": match.team1.name,
                "team2_name": match.team2.name,
                "match_date": date_label,
                "match_title": match_title,
                "team1_players": list(
                    team1_players.values(
                        "player_id",
                        "player__first_name",
                        "player__last_name",
                    )
                ),
                "team2_players": list(
                    team2_players.values(
                        "player_id",
                        "player__first_name",
                        "player__last_name",
                    )
                ),
            }
        )
