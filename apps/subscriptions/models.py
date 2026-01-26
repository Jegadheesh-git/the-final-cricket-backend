from django.db import models
from django.utils import timezone

class Plan(models.Model):
    OWNER_CHOICES = (
        ("USER","User"),
        ("ORG","Organization"),
    )

    BILLING_CYCLE_CHOICES = (
        ("MONTHLY","Monthly"),
        ("YEARLY","Yearly"),
    )

    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)

    owner_type = models.CharField(max_length=10, choices=OWNER_CHOICES)
    billing_cycle = models.CharField(max_length=10, choices=BILLING_CYCLE_CHOICES)

    razorpay_plan_id = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    toolUrl = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name 
    
class Subscription(models.Model):
    STATUS_CHOICES = (
        ("ACTIVE", "Active"),
        ("PENDING", "Pending"),
        ("CANCELLED", "Cancelled"),
        ("EXPIRED", "Expired"),
    )

    owner_type = models.CharField(max_length=10, choices=(('USER','User'),('ORG','Organization')))
    owner_id = models.UUIDField()

    plan = models.ForeignKey(Plan, on_delete=models.PROTECT)
    razorpay_subscription_id = models.CharField(max_length=100, null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="ACTIVE")

    current_period_start = models.DateTimeField(default=timezone.now)
    current_period_end = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    change_type = models.CharField(
        max_length = 10,
        choices= (("UPGRADE","Upgrade"),("DOWNGRADE","Downgrade")),
        null=True,
        blank=True
    )

    pending_plan = models.ForeignKey(
        Plan, 
        null=True, 
        blank=True,
        on_delete=models.SET_NULL,
        related_name="pending_subscriptions"    
    )

    class Meta:
        indexes = [
            models.Index(fields=["owner_type", "owner_id"])
        ]

    def is_active(self):
        if self.status != "ACTIVE":
            return False
        
        if self.current_period_end and self.current_period_end < timezone.now():
            return False
        
        return True