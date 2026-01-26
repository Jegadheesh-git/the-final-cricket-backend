from django.db import models
from django.contrib.auth.models import AbstractUser
from organizations.models import Organization
import uuid

class User(AbstractUser):

    ROLE_CHOICES = (
        ("OWNER","owner"),
        ("ADMIN","admin"),
        ("MEMBER","member")
    )

    organization = models.ForeignKey(Organization, null=True, blank=True, on_delete=models.SET_NULL)
    role = models.CharField(max_length=10,choices=ROLE_CHOICES, default="OWNER")
    allow_system_data = models.BooleanField(default=True)

class Device(models.Model):
    DEVICE_TYPE_CHOICE = (("DESKTOP","Desktop"),)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    owner_type = models.CharField(max_length=10, choices=(("USER","User"),("ORG","Organization")))
    owner_id = models.UUIDField()

    device_name = models.CharField(max_length=100)
    device_type = models.CharField(max_length=20, choices=DEVICE_TYPE_CHOICE)

    last_seen = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    

    class Meta:
        indexes = [
            models.Index(fields=["owner_type","owner_id"]),
        ]