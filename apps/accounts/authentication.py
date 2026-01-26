from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import Device

class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return 
    
class DeviceJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        result = super().authenticate(request)
        if not result:
            return None
        
        user, token = result
        device_id = token.get("device_id")

        if not Device.objects.filter(
            id = device_id,
            is_active = True
        ).exists():
            raise AuthenticationFailed("Device revoked")
        
        return user, token