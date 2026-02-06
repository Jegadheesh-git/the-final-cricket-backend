"""
SERIALIZER: Start Scoring Session Response

RESPONSIBILITY:
- Shape response after session initialisation
- Expose only required identifiers

MUST NEVER DO:
- Include derived stats
"""

from rest_framework import serializers


class StartScoringSessionResponseSerializer(serializers.Serializer):
    match_id = serializers.UUIDField()
    innings_id = serializers.UUIDField()
    innings_number = serializers.IntegerField()
