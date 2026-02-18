"""
SERVICE: Match Context Engine (Pure)

RESPONSIBILITY:
- Compute team totals by innings (non super-over)
- Compute chase targets for limited overs and Tests
"""
from scoring.models import InningsAggregate
from matches.models import Innings


def compute_team_totals(*, match):
    totals = {match.team1_id: 0, match.team2_id: 0}
    innings_qs = Innings.objects.filter(
        match=match,
        is_super_over=False,
    )
    for inn in innings_qs:
        aggregate = InningsAggregate.objects.filter(innings=inn).first()
        if not aggregate:
            continue
        totals[inn.batting_team_id] += aggregate.runs
    return totals


def compute_team_innings_counts(*, match):
    counts = {match.team1_id: 0, match.team2_id: 0}
    innings_qs = Innings.objects.filter(
        match=match,
        is_super_over=False,
    )
    for inn in innings_qs:
        if inn.state == Innings.State.COMPLETED:
            counts[inn.batting_team_id] += 1
    return counts


def compute_limited_overs_target(*, match):
    totals = compute_team_totals(match=match)
    return max(totals.values())


def compute_fourth_innings_target(*, match, batting_team_id):
    totals = compute_team_totals(match=match)
    batting_total = totals.get(batting_team_id, 0)
    opponent_total = (
        totals.get(match.team1_id, 0)
        if batting_team_id == match.team2_id
        else totals.get(match.team2_id, 0)
    )
    return (opponent_total - batting_total)
