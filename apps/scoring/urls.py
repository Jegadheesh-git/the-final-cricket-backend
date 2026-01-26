from django.urls import path
from scoring.views import (
    StartScoringSessionAPIView,
    InningsSetupAPIView,
    BallSubmissionAPIView,
    UndoLastBallAPIView,
    ApplyDLSAPIView,
    EndInningsAPIView,
    NextInningsAPIView,
    EndMatchAPIView,
)
from .views.video_upload import VideoUploadView


urlpatterns = [
    # Session
    path('matches/<uuid:match_id>/session/', StartScoringSessionAPIView.as_view(), name='start_scoring_session'),
    path('innings/<int:innings_id>/setup/', InningsSetupAPIView.as_view(), name='setup_innings'),
    
    # Ball Actions
    path('balls/submit/', BallSubmissionAPIView.as_view(), name='submit_ball'), # Assuming BallSubmissionAPIView is intended for SubmitBallAPIView
    path('balls/<uuid:ball_id>/video/', VideoUploadView.as_view(), name='upload_ball_video'),
    
    # Transitions
    path('innings/<int:innings_id>/end/', EndInningsAPIView.as_view(), name='end_innings'),
    path('matches/<uuid:match_id>/next-innings/', NextInningsAPIView.as_view(), name='next_innings'),
    path('matches/<uuid:match_id>/end/', EndMatchAPIView.as_view(), name='end_match'),
    
    # Utilities
    path('innings/<int:innings_id>/dls/', ApplyDLSAPIView.as_view(), name='apply_dls'),
]
