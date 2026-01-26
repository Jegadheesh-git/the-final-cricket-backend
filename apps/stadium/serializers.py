from rest_framework.serializers import ModelSerializer
from .models import Stadium

class StadiumSerializer(ModelSerializer):
    class Meta:
        model = Stadium
        fields = "__all__"
        read_only_fields = (
            "owner_type",
            "owner_id",
            "created_by",
            "created_at"
        )