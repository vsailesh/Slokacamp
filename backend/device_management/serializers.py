from rest_framework import serializers
from .models import Device, VideoSession, AuditLog
from accounts.serializers import UserSerializer

class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = '__all__'
        read_only_fields = ('user', 'last_accessed', 'created_at')

class DeviceRegisterSerializer(serializers.Serializer):
    device_id = serializers.CharField(max_length=255)
    device_name = serializers.CharField(max_length=255)
    platform = serializers.ChoiceField(choices=['web', 'android', 'ios'])

class DeviceTransferSerializer(serializers.Serializer):
    new_device_id = serializers.CharField(max_length=255)
    new_device_name = serializers.CharField(max_length=255)
    platform = serializers.ChoiceField(choices=['web', 'android', 'ios'])

class VideoSessionSerializer(serializers.ModelSerializer):
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)
    
    class Meta:
        model = VideoSession
        fields = '__all__'
        read_only_fields = ('user', 'device', 'session_token', 'started_at', 'last_heartbeat')

class VideoStartSerializer(serializers.Serializer):
    lesson_id = serializers.UUIDField()
    device_id = serializers.CharField(max_length=255)

class VideoHeartbeatSerializer(serializers.Serializer):
    session_token = serializers.CharField(max_length=255)
    current_time = serializers.IntegerField(help_text='Current playback position in seconds')

class AuditLogSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = '__all__'
        read_only_fields = ('created_at',)
