from rest_framework import serializers

class InningsSetupSerializer(serializers.Serializer):
    striker = serializers.UUIDField()
    non_striker = serializers.UUIDField()
    bowler = serializers.UUIDField()
