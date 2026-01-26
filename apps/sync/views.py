from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import SyncOperation
from .services import apply_operation, get_offline_match_context, process_bulk_sync
from .serializers import OfflineMatchContextSerializer, BulkSyncRequestSerializer

class SyncView(APIView):
    def post(self, request):
        scope = request.scope
        device_id = request.data.get("device_id")
        operations = request.data.get("operations",[])

        results = []

        for op in operations:
            result = apply_operation(
                scope = scope,
                device_id = device_id,
                op = op
            )
            results.append(result)

        return Response({
            "results": results
        })

class OfflineMatchContextAPIView(APIView):
    def get(self, request, match_id):
        # Permission check? IsAuthenticated is likely default.
        # Should we verify if user has access to this match? 
        # Match is publicly readable or Org restricted? 
        # For now assume Standard permissions apply.
        
        data = get_offline_match_context(match_id)
        serializer = OfflineMatchContextSerializer(data)
        return Response(serializer.data)

class BulkSyncAPIView(APIView):
    def post(self, request):
        serializer = BulkSyncRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        user = request.user
        
        try:
            result = process_bulk_sync(data, user)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )