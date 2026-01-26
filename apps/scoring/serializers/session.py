from rest_framework import serializers

class ScoringSessionSerializer(serializers.Serializer):
    session_type = serializers.ChoiceField(
        choices=["FRESH", "RESUME"]
    )

    match = serializers.DictField()
    match_type = serializers.DictField()

    innings = serializers.DictField(
        required=False, allow_null=True
    )

    current_state = serializers.DictField(
        required=False, allow_null=True
    )

    available_players = serializers.DictField()
