from django.db import models
from django.conf import settings
import uuid
from django.utils import timezone
import secrets

class Video(models.Model):
    """Video content with DRM protection and streaming capabilities"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Basic video information
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Video file management
    original_filename = models.CharField(max_length=255)
    file_size = models.BigIntegerField(help_text='File size in bytes')
    duration = models.PositiveIntegerField(help_text='Duration in seconds')
    
    # Storage locations
    s3_bucket = models.CharField(max_length=255)
    s3_key = models.CharField(max_length=500)  # Path to master file in S3
    
    # Video quality and formats
    resolution = models.CharField(max_length=20, choices=[
        ('240p', '240p'),
        ('360p', '360p'),
        ('480p', '480p'),
        ('720p', '720p'),
        ('1080p', '1080p'),
        ('1440p', '1440p'),
        ('2160p', '2160p (4K)'),
    ])
    
    # Video processing status
    processing_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ], default='pending')
    
    # DRM and streaming configuration
    drm_enabled = models.BooleanField(default=True)
    vdocipher_video_id = models.CharField(max_length=255, blank=True, null=True)
    
    # HLS/DASH streaming URLs
    hls_url = models.URLField(blank=True)
    dash_url = models.URLField(blank=True)
    
    # Video thumbnails and previews
    thumbnail_url = models.URLField(blank=True)
    preview_gif_url = models.URLField(blank=True)
    
    # Video metadata
    video_codec = models.CharField(max_length=50, blank=True)
    audio_codec = models.CharField(max_length=50, blank=True)
    bitrate = models.PositiveIntegerField(blank=True, null=True, help_text='Bitrate in kbps')
    frame_rate = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    aspect_ratio = models.CharField(max_length=20, blank=True)
    
    # Content classification
    content_type = models.CharField(max_length=50, choices=[
        ('lecture', 'Lecture'),
        ('demonstration', 'Demonstration'),
        ('meditation', 'Guided Meditation'),
        ('chanting', 'Sanskrit Chanting'),
        ('interview', 'Interview'),
        ('documentary', 'Documentary'),
    ])
    
    # Language and accessibility
    primary_language = models.CharField(max_length=10, default='en')
    has_subtitles = models.BooleanField(default=False)
    subtitle_languages = models.JSONField(default=list, blank=True)
    has_transcript = models.BooleanField(default=False)
    
    # Access control
    is_public = models.BooleanField(default=False)
    requires_subscription = models.BooleanField(default=True)
    
    # Analytics
    view_count = models.PositiveIntegerField(default=0)
    total_watch_time = models.BigIntegerField(default=0)  # Total watch time across all users in seconds
    average_watch_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    
    # SEO and discoverability
    tags = models.JSONField(default=list, blank=True)
    
    # Timestamps
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'videos'
        verbose_name = 'Video'
        verbose_name_plural = 'Videos'
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['processing_status']),
            models.Index(fields=['content_type', 'is_public']),
            models.Index(fields=['-view_count']),
        ]
    
    def __str__(self):
        return self.title

class PlaybackSession(models.Model):
    """Track video playback sessions for analytics and device enforcement"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Session identification
    session_token = models.CharField(max_length=64, unique=True, db_index=True)
    
    # Related entities
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='playback_sessions')
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='playback_sessions')
    device = models.ForeignKey('devices.Device', on_delete=models.CASCADE, related_name='playback_sessions')
    
    # Lesson context (if video is part of a lesson)
    lesson = models.ForeignKey('courses.Lesson', on_delete=models.CASCADE, blank=True, null=True, related_name='playback_sessions')
    
    # Session status
    status = models.CharField(max_length=20, choices=[
        ('started', 'Started'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('abandoned', 'Abandoned'),
        ('terminated', 'Terminated'),  # Forcibly ended
    ], default='started')
    
    # Playback tracking
    start_position = models.PositiveIntegerField(default=0)  # Start position in seconds
    current_position = models.PositiveIntegerField(default=0)  # Current position in seconds
    end_position = models.PositiveIntegerField(default=0)  # End position in seconds
    watch_duration = models.PositiveIntegerField(default=0)  # Actual watch time in seconds
    
    # Quality and technical metrics
    video_quality = models.CharField(max_length=20, blank=True)
    bandwidth = models.PositiveIntegerField(blank=True, null=True, help_text='Bandwidth in kbps')
    buffer_events = models.PositiveIntegerField(default=0)
    
    # Security and enforcement
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    screen_recording_detected = models.BooleanField(default=False)
    concurrent_sessions_detected = models.BooleanField(default=False)
    
    # DRM information
    drm_session_id = models.CharField(max_length=255, blank=True)
    license_requests = models.PositiveIntegerField(default=0)
    
    # Heartbeat tracking
    last_heartbeat_at = models.DateTimeField(auto_now=True)
    heartbeat_interval = models.PositiveIntegerField(default=30)  # Heartbeat interval in seconds
    missed_heartbeats = models.PositiveIntegerField(default=0)
    
    # Session timestamps
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'playback_sessions'
        verbose_name = 'Playback Session'
        verbose_name_plural = 'Playback Sessions'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['video', 'status']),
            models.Index(fields=['device', 'status']),
            models.Index(fields=['session_token']),
            models.Index(fields=['-started_at']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.video.title} ({self.status})"
    
    def save(self, *args, **kwargs):
        if not self.session_token:
            self.session_token = secrets.token_urlsafe(32)
        super().save(*args, **kwargs)
    
    def is_active(self):
        """Check if session is considered active based on last heartbeat"""
        if self.status not in ['started', 'active', 'paused']:
            return False
        
        time_since_heartbeat = timezone.now() - self.last_heartbeat_at
        return time_since_heartbeat.seconds < (self.heartbeat_interval * 3)  # Allow 3 missed heartbeats
    
    def terminate(self, reason='unknown'):
        """Terminate the playback session"""
        self.status = 'terminated'
        self.ended_at = timezone.now()
        self.save(update_fields=['status', 'ended_at'])

class VideoAnalytics(models.Model):
    """Aggregate video analytics data"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='analytics')
    
    # Time period for analytics
    date = models.DateField()
    
    # View metrics
    unique_viewers = models.PositiveIntegerField(default=0)
    total_views = models.PositiveIntegerField(default=0)
    total_watch_time = models.BigIntegerField(default=0)  # in seconds
    
    # Engagement metrics
    completion_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    average_watch_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    replay_count = models.PositiveIntegerField(default=0)
    
    # Quality metrics
    buffer_ratio = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    average_bitrate = models.PositiveIntegerField(default=0)
    
    # Device and platform breakdown
    ios_views = models.PositiveIntegerField(default=0)
    android_views = models.PositiveIntegerField(default=0)
    web_views = models.PositiveIntegerField(default=0)
    
    # Geographic data (if available)
    top_countries = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'video_analytics'
        verbose_name = 'Video Analytics'
        verbose_name_plural = 'Video Analytics'
        unique_together = [['video', 'date']]
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.video.title} - Analytics ({self.date})"