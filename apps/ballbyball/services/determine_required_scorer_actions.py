"""
SERVICE: Determine Required Scorer Actions

RESPONSIBILITY:
- Decide what the scorer MUST do before next save
- Examples: select striker, select bowler, end innings

MUST DO:
- Inspect current authoritative state
- Return boolean action flags

MUST NEVER DO:
- Modify database
- Save balls
- Perform calculations
"""
def determine_required_scorer_actions(
    *,
    state,
    innings_end=False,
    match_end=False,
    ask_follow_on=False,
    confirm_super_over=False,
):
    agg = state["aggregate"]
    striker_missing = agg["current_striker"] is None
    non_striker_missing = agg["current_non_striker"] is None
    bowler_missing = agg["current_bowler"] is None
    return {
        "striker_select": striker_missing,
        "non_striker_select": non_striker_missing,
        "bowler_select": bowler_missing,
        "new_batter_select": striker_missing or non_striker_missing,
        "new_bowler_select": bowler_missing,
        "new_striker_required": striker_missing,
        "new_non_striker_required": non_striker_missing,
        "end_innings": innings_end,
        "end_match": match_end,
        "ask_follow_on": ask_follow_on,
        "confirm_super_over": confirm_super_over,
    }
