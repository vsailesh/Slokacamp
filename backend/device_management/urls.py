from django.urls import path
from .views import (
    DeviceListView, DeviceRegisterView, DeviceTransferView, DeviceRevokeView,
    VideoStartView, VideoHeartbeatView, VideoEndView, AuditLogListView
)

app_name = 'device_management'

urlpatterns = [
    # Device Management
    path('devices/', DeviceListView.as_view(), name='device_list'),
    path('devices/register/', DeviceRegisterView.as_view(), name='device_register'),
    path('devices/transfer/', DeviceTransferView.as_view(), name='device_transfer'),
    path('devices/<uuid:pk>/revoke/', DeviceRevokeView.as_view(), name='device_revoke'),
    
    # Video Session Management
    path('video/start/', VideoStartView.as_view(), name='video_start'),
    path('video/heartbeat/', VideoHeartbeatView.as_view(), name='video_heartbeat'),
    path('video/end/', VideoEndView.as_view(), name='video_end'),
    
    # Audit Logs
    path('audit-logs/', AuditLogListView.as_view(), name='audit_logs'),
]
