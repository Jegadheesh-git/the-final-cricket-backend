from django.db import models
import uuid

class SyncOperation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    owner_type = models.CharField(max_length=10)
    owner_id = models.UUIDField()

    device_id = models.UUIDField()
    entity = models.CharField(max_length=50)
    operation = models.CharField(
        max_length=10,
        choices = (("CREATE","CREATE"),("UPDATE","UPDATE"),("DELETE","DELETE"))
    )

    sync_id = models.UUIDField()
    payload = models.UUIDField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("device_id","sync_id","operation")
