from django.urls import path
from .views import SyncView, OfflineMatchContextAPIView, BulkSyncAPIView

urlpatterns = [
    path('ops/', SyncView.as_view(), name='sync_ops'),
    path('matches/<uuid:match_id>/context/', OfflineMatchContextAPIView.as_view(), name='offline_match_context'),
    path('commit/', BulkSyncAPIView.as_view(), name='bulk_sync_commit'),
]
