from rest_framework import serializers

class BallOutcomeSerializer(serializers.Serializer):
    ball_id = serializers.UUIDField()

    events = serializers.DictField()
    actions_required = serializers.DictField()
    next_state = serializers.DictField(allow_null=True)
    aggregates = serializers.DictField()
