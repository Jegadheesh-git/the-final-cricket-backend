"""
SERIALIZER: Ball Delivery State Response

RESPONSIBILITY:
- Shape authoritative response after save/undo
- Include aggregates, stats, and actions

MUST NEVER DO:
- Modify state
"""
from rest_framework import serializers


class BallDeliveryStateResponseSerializer(serializers.Serializer):
    match_id = serializers.UUIDField()
    innings_id = serializers.IntegerField()

    aggregate = serializers.DictField()
    batting_stats = serializers.ListField()
    bowling_stats = serializers.ListField()
    players = serializers.DictField()
    penalties = serializers.ListField(required=False)
    actions = serializers.DictField()
    events = serializers.DictField(required=False)
    next_state = serializers.DictField(required=False)
