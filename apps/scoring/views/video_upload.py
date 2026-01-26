from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os

from scoring.models.ball import Ball
from scoring.models.video import BallVideo

class VideoUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, ball_id):
        ball = get_object_or_404(Ball, id=ball_id)
        
        file_obj = request.FILES.get('video')
        if not file_obj:
            return Response({"error": "No video file provided"}, status=status.HTTP_400_BAD_REQUEST)

        # Logic to save file
        match_id = str(ball.match.id)
        file_ext = os.path.splitext(file_obj.name)[1]
        file_name = f"videos/match_{match_id}/ball_{ball_id}{file_ext}"
        
        # If file exists, default_storage.save usually appends hash. We might want to overwrite?
        # For simplicity, let it handle uniquess.
        
        if default_storage.exists(file_name):
            default_storage.delete(file_name)
            
        path = default_storage.save(file_name, ContentFile(file_obj.read()))
        
        # Create or Update BallVideo
        # Note: video_start_ms/end_ms are required fields. 
        # If updating, we keep existing. If creating, we need defaults or input.
        
        defaults = {
            "video_start_ms": request.data.get('start_ms', 0),
            "video_end_ms": request.data.get('end_ms', 0),
            "video_source_id": path
        }
        
        video, created = BallVideo.objects.update_or_create(
            ball=ball,
            defaults=defaults
        )
        
        return Response({
            "status": "UPLOADED",
            "video_path": path,
            "ball_id": str(ball_id)
        }, status=status.HTTP_201_CREATED)
