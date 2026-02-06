"""
SERVICE: Validate Match and Scorer Ownership

RESPONSIBILITY:
- Ensure match exists
- Ensure match belongs to user's organisation
- Ensure user has permission to score

MUST DO:
- Raise domain exceptions on failure

MUST NEVER DO:
- Modify database state
- Decide cricket outcomes
"""

from rest_framework.exceptions import PermissionDenied


def validate_match_and_scorer_ownership(*, user, match):
    """
    Validate that the given user is allowed to score this match.
    """
    print(user.id)
    # Example rule: match is owned by organisation
    if ((match.owner_id != user.organization_id and match.owner_type =="ORG") ):
        
        raise PermissionDenied("You are not allowed to score this match")

    # Future: role-based checks can be added here
