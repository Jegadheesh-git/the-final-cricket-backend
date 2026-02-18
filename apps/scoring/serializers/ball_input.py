from rest_framework import serializers

class BallInputSerializer(serializers.Serializer):
    innings = serializers.IntegerField()
    ball_number = serializers.IntegerField(min_value=1)
    over_number = serializers.IntegerField(min_value=1)
    ball_in_over = serializers.IntegerField(min_value=1)

    striker = serializers.UUIDField()
    non_striker = serializers.UUIDField()
    bowler = serializers.UUIDField()
    striker_hand = serializers.ChoiceField(
        choices=("LEFT", "RIGHT"),
        required=False,
        allow_null=True
    )
    bowler_hand = serializers.ChoiceField(
        choices=("LEFT", "RIGHT"),
        required=False,
        allow_null=True
    )
    umpire_bowler_end = serializers.UUIDField(required=False, allow_null=True)
    umpire_square_leg = serializers.UUIDField(required=False, allow_null=True)
    drs = serializers.DictField(required=False)

    runs = serializers.DictField()
    wicket = serializers.DictField(required=False, allow_null=True)

    analytics = serializers.DictField(required=False, allow_null=True)
    spatial = serializers.DictField(required=False, allow_null=True)
    trajectory = serializers.DictField(required=False, allow_null=True)
    release = serializers.DictField(required=False, allow_null=True)
    video = serializers.DictField(required=False, allow_null=True)
