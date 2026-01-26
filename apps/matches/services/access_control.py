def assert_user_can_access_match(user, match):
    if match.owner_org:
        if user.organization_id != match.owner_org_id:
            raise PermissionError("Access denied")
    else:
        if match.owner_user_id != user.id:
            raise PermissionError("Access denied")
