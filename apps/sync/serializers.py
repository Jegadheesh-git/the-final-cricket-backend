from rest_framework import serializers

class PlayerValidationSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    role = serializers.CharField()
    batting_hand = serializers.CharField()
    bowling_hand = serializers.CharField()
    # Add other fields as needed for offline UI

class TeamLiteSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    short_name = serializers.CharField()
    squad = PlayerValidationSerializer(many=True)

class OfflineMatchContextSerializer(serializers.Serializer):
    match_id = serializers.UUIDField()
    match_type = serializers.DictField() # Rules
    teams = serializers.DictField(child=TeamLiteSerializer()) # { "team1": ..., "team2": ... }
    # We might need playing_xi if it exists, but user said it's created offline.
    # If it exists (resume), we should send it.
    playing_xi = serializers.DictField(required=False, allow_null=True) 
    
class BulkSyncItemSerializer(serializers.Serializer):
    # This mirrors the online BallInputSerializer but strictly for order-preserving replay
    ball_number = serializers.IntegerField()
    # We need full ball data. 
    # Actually, we can reuse BallInputSerializer validation logic? 
    # But this is a bulk list committed at once.
    
    # Let's keep it generic for now and validate in service
    payload = serializers.DictField() 

class BulkSyncRequestSerializer(serializers.Serializer):
    match_id = serializers.UUIDField()
    sync_token = serializers.CharField(required=False) # For idempotent/dedup
    balls = serializers.ListField(child=serializers.DictField()) 
    # Events like Toss, PlayingXI creation might need to be synced too if done offline?
    # User said: "toss and playingXi iteself will be created offline only"
    # So we need to sync those events BEFORE balls.
    
    events = serializers.ListField(child=serializers.DictField(), required=False)
    # events schema: { "type": "TOSS_DECISION", "payload": {...} }
