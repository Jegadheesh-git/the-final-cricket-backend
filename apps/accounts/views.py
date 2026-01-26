from django.contrib.auth import login, logout, authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import ValidationError
from .serializers import LoginSerializer, RegisterSerializer, RegisterOrganizationSerializer
from .models import Device
from subscriptions.capabilities import PLAN_CAPABILITIES
from django.utils import timezone
from .tokens import create_device_token

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        login(request, user)

        # Determine account type and organization info
        account_type = "organization" if user.organization else "solo"
        organization_name = user.organization.name if user.organization else None
        organization_id = user.organization.id if user.organization else None
        
        return Response({
            "message": "Login Successful",
            "account_type": account_type,
            "organization_name": organization_name,
            "organization_id": organization_id,
            "role": user.role,
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name
        })

# views.py

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        from .serializers import RegisterSerializer, RegisterOrganizationSerializer
        
        account_type = request.data.get('accountType', 'solo')
        
        if account_type == 'organization':
            # Handle organization registration
            organization_data = request.data.get('organization', {})
            
            # Prepare data for serializer
            serializer_data = {
                'username': request.data.get('username'),
                'email': request.data.get('email'),
                'password': request.data.get('password'),
                'first_name': request.data.get('firstName'),
                'last_name': request.data.get('lastName'),
                'organization_name': organization_data.get('name'),
                'address': organization_data.get('address'),
                'city': organization_data.get('city'),
                'state': organization_data.get('state'),
                'pincode': organization_data.get('pincode'),
                'country': organization_data.get('country'),
                'contact_number': organization_data.get('contactNumber')
            }
            
            serializer = RegisterOrganizationSerializer(data=serializer_data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            
            login(request, user)
            return Response({
                "message": "Organization Registration Successful",
                "user_id": user.id,
                "organization_id": user.organization.id,
                "account_type": "organization"
            }, status=201)
        
        else:
            # Handle solo account registration
            serializer_data = {
                'username': request.data.get('username'),
                'email': request.data.get('email'),
                'password': request.data.get('password'),
                'first_name': request.data.get('firstName'),
                'last_name': request.data.get('lastName')
            }
            
            serializer = RegisterSerializer(data=serializer_data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            
            login(request, user)
            return Response({
                "message": "Registration Successful",
                "user_id": user.id,
                "account_type": "solo"
            }, status=201)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"message":"Logout Successful"})
    
class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_authenticated": True
        })
    
class DesktopLoginView(APIView):
    authentication_classes = [] #no session
    permission_classes = []

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        device_id = request.data.get("device_id")

        if not device_id:
            raise ValidationError("device_id is required")
        
        user = authenticate(username=username, password=password)
        if not user:
            raise ValidationError("Invalid credentials")
        
        #Validate device
        if not Device.objects.filter(
            id = device_id,
            is_active = True
        ).exists():
            raise ValidationError("Device not registered")
        
        token = create_device_token(
            user=user,
            device_id=device_id,
            scope=request.scope
        )

        return Response({
            "access_token": str(token),
            "expires_in": 900
        })



class RegisterDeviceView(APIView):
    def post(self, request):
        scope = request.scope
        device_id = request.data.get("device_id")
        device_name = request.data.get("device_name")

        if not device_id or not device_name:
            raise ValidationError("device_id and device_name required")

        #Already registered? 
        if Device.objects.filter(id=device_id, is_active=True).exists():
            return Response({"status":"ALREADY_REGISTERED"})
        
        subscription = scope.subscription
        if not subscription:
            raise ValidationError("No active subscription")
        
        plan_code = subscription.plan.code
        limits = PLAN_CAPABILITIES.get(plan_code,{}).get("limits",{})
        max_devices = limits.get("devices")

        if max_devices is not None:
            used = Device.objects.filter(
                owner_type = scope.owner_type,
                owner_id = scope.owner_id,
                is_active = True
            ).count()

            if used >= max_devices:
                raise ValidationError("Device limit reached")
            
        Device.objects.create(
            id = device_id,
            owner_type = scope.owner_type,
            owner_id = scope.owner_id,
            device_name = device_name,
            device_type = "DESKTOP",
        )

        return Response({"status":"REGISTERED"})
    

class DeviceHeartbeatView(APIView):
    def post(self, request):
        device_id = request.data.get("device_id")

        Device.objects.filter(id=device_id).update(
            last_seen = timezone.now()
        )

        return Response({"status":"OK"})
    
class RevokeDevices(APIView):
    def post(self, request):
        scope = request.scope
        device_id = request.data.get("device_id")

        Device.objects.filter(
            id=device_id,
            owner_type = scope.owner_type,
            owner_id = scope.owner_id
        ).update(is_active=False)

        return Response({"status":"REVOKED"})