from django.db import models
from django.conf import settings
import uuid

class Device(models.Model):
    PLATFORM_CHOICES = (
        ('web', 'Web'),
        ('android', 'Android'),
        ('ios', 'iOS'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='devices', on_delete=models.CASCADE)
    device_id = models.CharField(max_length=255, unique=True)
    device_name = models.CharField(max_length=255)
    platform = models.CharField(max_length=10, choices=PLATFORM_CHOICES)
    is_active = models.BooleanField(default=True)
    last_accessed = models.DateTimeField(auto_now=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'devices'
        ordering = ['-last_accessed']

    def __str__(self):
        return f"{self.user.email} - {self.device_name}"


class VideoSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='video_sessions', on_delete=models.CASCADE)
    device = models.ForeignKey(Device, related_name='video_sessions', on_delete=models.CASCADE)
    lesson = models.ForeignKey('courses.Lesson', related_name='sessions', on_delete=models.CASCADE)
    session_token = models.CharField(max_length=255, unique=True)
    started_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    last_heartbeat = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'video_sessions'
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.user.email} - {self.lesson.title}"


class AuditLog(models.Model):
    ACTION_CHOICES = (
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('device_change', 'Device Change'),
        ('video_start', 'Video Start'),
        ('video_end', 'Video End'),
        ('payment', 'Payment'),
        ('subscription', 'Subscription'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='audit_logs', on_delete=models.CASCADE, null=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    ip_address = models.GenericIPAddressField(null=True)
    user_agent = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'audit_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f"{self.action} - {self.user.email if self.user else 'System'}"
