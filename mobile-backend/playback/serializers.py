from rest_framework import serializers
from .models import PlaybackSession
from videos.models import Video
from devices.models import Device
from courses.models import Lesson

class PlaybackStartSerializer(serializers.Serializer):
    """Serializer for starting a playback session"""
    video_id = serializers.UUIDField()
    device_id = serializers.UUIDField()
    lesson_id = serializers.UUIDField(required=False, allow_null=True)
    start_position = serializers.IntegerField(default=0, min_value=0)
    
    def validate_video_id(self, value):
        try:
            Video.objects.get(id=value, processing_status='completed')
        except Video.DoesNotExist:
            raise serializers.ValidationError("Video not found or not ready")
        return value
    
    def validate_device_id(self, value):
        request = self.context.get('request')
        if request:
            try:
                Device.objects.get(
                    id=value,
                    user=request.user,
                    is_active=True
                )
            except Device.DoesNotExist:
                raise serializers.ValidationError("Invalid or inactive device")
        return value
    
    def validate_lesson_id(self, value):
        if value:
            try:
                Lesson.objects.get(id=value, is_published=True)
            except Lesson.DoesNotExist:
                raise serializers.ValidationError("Lesson not found")
        return value

class PlaybackHeartbeatSerializer(serializers.Serializer):
    """Serializer for playback heartbeat"""
    session_token = serializers.CharField(max_length=64)
    current_position = serializers.IntegerField(min_value=0)
    buffer_events = serializers.IntegerField(default=0, min_value=0)
    video_quality = serializers.CharField(max_length=20, required=False, allow_blank=True)
    screen_recording_detected = serializers.BooleanField(default=False)
    bandwidth = serializers.IntegerField(required=False, allow_null=True)

class PlaybackEndSerializer(serializers.Serializer):
    """Serializer for ending a playback session"""
    session_token = serializers.CharField(max_length=64)
    end_position = serializers.IntegerField(min_value=0)
    completion_percentage = serializers.FloatField(min_value=0.0, max_value=100.0, default=0.0)

class PlaybackSessionSerializer(serializers.ModelSerializer):
    """Serializer for playback session details"""
    video_title = serializers.CharField(source='video.title', read_only=True)
    device_name = serializers.CharField(source='device.device_name', read_only=True)
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)
    
    class Meta:
        model = PlaybackSession
        fields = [
            'id', 'session_token', 'video_title', 'device_name',
            'lesson_title', 'status', 'start_position', 'current_position',
            'end_position', 'watch_duration', 'video_quality',
            'screen_recording_detected', 'started_at', 'ended_at',
            'last_heartbeat_at'
        ]
        read_only_fields = [
            'id', 'session_token', 'started_at', 'ended_at',
            'last_heartbeat_at'
        ]