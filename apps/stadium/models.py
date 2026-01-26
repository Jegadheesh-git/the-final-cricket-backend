from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class Stadium(models.Model):

    name = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    
    owner_type = models.CharField(max_length=10, choices=(
        ("USER", "user"),
        ("ORG", "organisation")
    ))
    owner_id = models.UUIDField()

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_players')
    created_at = models.DateTimeField(auto_now_add=True)

    sync_id = models.UUIDField(unique=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["owner_type","owner_id"])
        ]

    def __str__(self):
        return self.name
