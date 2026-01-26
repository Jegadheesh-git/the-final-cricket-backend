from rest_framework_simplejwt.tokens import AccessToken

def create_device_token(*, user, device_id, scope):
    token = AccessToken.for_user(user)

    token["device_id"] = str(device_id)
    token["owner_type"] = scope.owner_type
    token["owner_id"] = str(scope.owner_id)

    return token