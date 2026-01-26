import uuid
from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class Organization(models.Model):
    name = models.CharField(max_length=255)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="created_organizations")
    created_at = models.DateTimeField(auto_now_add=True)

    address = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=255, null=True, blank=True)
    pincode = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    contact_number = models.CharField(max_length=255, null=True, blank=True)


    allow_system_data = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    

class OrganizationInvite(models.Model):
    organization = models.ForeignKey(
        Organization, on_delete= models.CASCADE, related_name="invites"
    )
    email = models.EmailField()
    role = models.CharField(max_length=10, choices=(
        ("ADMIN", "admin"),("MEMBER","member")
    ))
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("organization","email")