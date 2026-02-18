"""
SERIALIZER: Ball Delivery Input Payload

RESPONSIBILITY:
- Validate shape of incoming ball payload
- Ensure required fields are present

MUST NEVER DO:
- Validate cricket legality
- Apply business rules
"""
from rest_framework import serializers


class BallDeliveryInputPayloadSerializer(serializers.Serializer):
    match_id = serializers.UUIDField()
    striker = serializers.UUIDField()
    non_striker = serializers.UUIDField()
    bowler = serializers.UUIDField()

    completed_runs = serializers.IntegerField(min_value=0, default=0)
    is_wide = serializers.BooleanField(default=False)
    is_no_ball = serializers.BooleanField(default=False)
    is_bye = serializers.BooleanField(default=False)
    is_leg_bye = serializers.BooleanField(default=False)
    is_boundary = serializers.BooleanField(default=False)
    is_short_run = serializers.BooleanField(default=False)
    is_quick_running = serializers.BooleanField(default=False)
    is_free_hit = serializers.BooleanField(default=False)
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

    wicket_type = serializers.CharField(required=False, allow_null=True)
    dismissed_player_id = serializers.UUIDField(required=False, allow_null=True)
    dismissed_by_id = serializers.UUIDField(required=False, allow_null=True)
    caught_by_id = serializers.UUIDField(required=False, allow_null=True)
    stumped_by_id = serializers.UUIDField(required=False, allow_null=True)
    run_out_fielder_1_id = serializers.UUIDField(required=False, allow_null=True)
    run_out_fielder_2_id = serializers.UUIDField(required=False, allow_null=True)

    analytics = serializers.DictField(required=False)
    spatial = serializers.DictField(required=False)
    release = serializers.DictField(required=False)
    video = serializers.DictField(required=False)
    trajectory = serializers.ListField(
        child=serializers.DictField(),
        required=False
    )
    fielding = serializers.DictField(required=False)
    drs = serializers.DictField(required=False)
