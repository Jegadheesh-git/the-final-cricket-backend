from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User
from organizations.models import Organization
from django.db import transaction

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only = True)

    def validate(self, data):
        user = authenticate(
            username = data["username"],
            password = data["password"]
        )

        if not user:
            raise serializers.ValidationError("Invalid username or password!")
        if not user.is_active:
            raise serializers.ValidationError("User account is disabled!")
        
        data["user"] = user
        return data

# serializers.py

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta:
        from .models import User
        model = User
        fields = ('username', 'email', 'password', 'first_name', 'last_name')

    def create(self, validated_data):
        from .models import User
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            password=validated_data['password'],
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name')
        )
        return user


class RegisterOrganizationSerializer(serializers.Serializer):
    # User fields
    username = serializers.EmailField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    
    # Organization fields
    organization_name = serializers.CharField(required=True)
    address = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField(required=False, allow_blank=True)
    state = serializers.CharField(required=False, allow_blank=True)
    pincode = serializers.CharField(required=False, allow_blank=True)
    country = serializers.CharField(required=False, allow_blank=True)
    contact_number = serializers.CharField(required=False, allow_blank=True)

    def create(self, validated_data):
        
        with transaction.atomic():
            # Create user first (without organization)
            user = User.objects.create_user(
                username=validated_data['username'],
                email=validated_data['email'],
                password=validated_data['password'],
                first_name=validated_data['first_name'],
                last_name=validated_data['last_name'],
                role='OWNER'  # Organization creator is OWNER
            )
            
            # Create organization
            organization = Organization.objects.create(
                name=validated_data['organization_name'],
                created_by=user,
                address=validated_data.get('address', ''),
                city=validated_data.get('city', ''),
                state=validated_data.get('state', ''),
                pincode=validated_data.get('pincode', ''),
                country=validated_data.get('country', ''),
                contact_number=validated_data.get('contact_number', '')
            )
            
            # Link organization to user
            user.organization = organization
            user.save()
            
        return user