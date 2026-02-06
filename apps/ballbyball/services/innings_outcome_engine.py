"""
SERVICE: Innings & Match Outcome Engine (Pure)

RESPONSIBILITY:
- Detect innings end
- Detect match end
- Decide follow-on requirement (Test only)
- Compute target status for chases

MUST DO:
- Be pure
- Not write to DB
"""


def detect_innings_end(*, aggregate, match_type):
    # All out
    if aggregate.wickets >= 10:
        return True

    # Overs exhausted (if limited)
    max_overs = aggregate.max_overs or match_type.max_overs
    if max_overs is not None:
        if aggregate.completed_overs >= max_overs:
            return True

    # Target achieved (chasing)
    effective_target = get_effective_target(aggregate=aggregate)
    if aggregate.is_chasing and effective_target is not None:
        if aggregate.runs > effective_target:
            return True

    return False


def detect_target_state(*, aggregate):
    if not aggregate.is_chasing or aggregate.target_runs is None:
        return None
    effective_target = get_effective_target(aggregate=aggregate)
    if effective_target is None:
        return None
    if aggregate.runs > effective_target:
        return "WON"
    if aggregate.runs == effective_target:
        return "TIED"
    return "IN_PROGRESS"


def detect_follow_on_required(*, match_type, innings_number):
    return (
        match_type.is_test and
        innings_number == 2 and
        match_type.follow_on_allowed
    )


def get_effective_target(*, aggregate):
    return aggregate.revised_target_runs or aggregate.target_runs


def detect_match_end(*, aggregate, match_type, innings_number, match=None):
    """
    Conservative match-end detection:
    - Always end if chase is decided (WON/TIED) once innings ends
    - Otherwise end when max innings completed
    """
    target_state = detect_target_state(aggregate=aggregate)
    if (
        aggregate.is_chasing and
        get_effective_target(aggregate=aggregate) is not None and
        target_state in ("WON", "TIED")
    ):
        return True

    if innings_number >= match_type.max_innings:
        return True

    # Test-specific: innings victory after 3rd innings
    if match and match_type.is_test and innings_number == 3:
        from ballbyball.services.match_context_engine import (
            compute_team_totals,
            compute_team_innings_counts,
        )
        totals = compute_team_totals(match=match)
        counts = compute_team_innings_counts(match=match)

        teams = list(totals.keys())
        team_a, team_b = teams[0], teams[1]

        if counts[team_a] == 2 and counts[team_b] == 1:
            return totals[team_a] < totals[team_b]
        if counts[team_b] == 2 and counts[team_a] == 1:
            return totals[team_b] < totals[team_a]

    return False
