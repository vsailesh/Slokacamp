from django.urls import path
from . import views

urlpatterns = [
    # Device management
    path('devices/', views.device_list, name='device-list'),
    path('devices/<uuid:device_id>/', views.device_detail, name='device-detail'),
    path('devices/<uuid:device_id>/heartbeat/', views.device_heartbeat, name='device-heartbeat'),
    
    # Device transfer
    path('devices/transfer/', views.device_transfer, name='device-transfer'),
    path('devices/set-primary/', views.set_primary_device, name='set-primary-device'),
    path('devices/transfer-history/', views.device_transfer_history, name='device-transfer-history'),
]