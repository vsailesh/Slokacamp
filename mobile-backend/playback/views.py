# Playback Session Management Views
# Handles video playback sessions, device validation, and DRM token generation

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.db import models
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import secrets

from .models import PlaybackSession
from .serializers import PlaybackSessionSerializer, PlaybackStartSerializer, PlaybackHeartbeatSerializer
from videos.models import Video
from videos.utils import VdoCipherIntegration, S3SignedURLGenerator
from devices.models import Device
from courses.models import Lesson, LessonProgress, Enrollment

@swagger_auto_schema(
    method='post',
    request_body=PlaybackStartSerializer,
    responses={
        201: openapi.Response(
            description='Playback session started',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'session_token': openapi.Schema(type=openapi.TYPE_STRING),
                    'video_urls': openapi.Schema(type=openapi.TYPE_OBJECT),
                    'drm_token': openapi.Schema(type=openapi.TYPE_OBJECT),
                    'expires_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
                }
            )
        ),
        400: 'Bad Request',
        403: 'Forbidden - Device not authorized or concurrent session detected',
        404: 'Video not found',
    },
    operation_description='Start a new video playback session with DRM protection'
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_playback(request):
    """Start a new video playback session with device validation and DRM"""
    serializer = PlaybackStartSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    video_id = serializer.validated_data['video_id']
    device_id = serializer.validated_data['device_id']
    lesson_id = serializer.validated_data.get('lesson_id')
    start_position = serializer.validated_data.get('start_position', 0)
    
    try:
        # Get video and validate access
        video = get_object_or_404(Video, id=video_id)
        
        # Validate device
        device = get_object_or_404(
            Device, 
            id=device_id, 
            user=request.user, 
            is_active=True
        )
        
        if not device.is_primary:
            return Response({
                'error': 'Device not authorized',
                'message': 'This device is not authorized for video playback. Please use your primary device.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Check for concurrent sessions
        active_sessions = PlaybackSession.objects.filter(
            user=request.user,
            status__in=['started', 'active', 'paused']
        ).exclude(device=device)
        
        if active_sessions.exists():
            # Terminate other sessions
            for session in active_sessions:
                session.terminate('concurrent_session_detected')
            
            return Response({
                'error': 'Concurrent session detected',
                'message': 'Video playback on another device has been terminated. Please try again.'
            }, status=status.HTTP_409_CONFLICT)
        
        # Validate subscription/access rights
        if video.requires_subscription and not request.user.is_subscription_active:
            return Response({
                'error': 'Subscription required',
                'message': 'This video requires an active subscription.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Validate lesson enrollment if applicable
        lesson = None
        if lesson_id:
            lesson = get_object_or_404(Lesson, id=lesson_id)
            
            # Check if user is enrolled in the course
            enrollment = Enrollment.objects.filter(
                user=request.user,
                course=lesson.course,
                status='active'
            ).first()
            
            if not enrollment:
                return Response({
                    'error': 'Course enrollment required',
                    'message': 'You must be enrolled in this course to watch this video.'
                }, status=status.HTTP_403_FORBIDDEN)
        
        # Generate session token
        session_token = secrets.token_urlsafe(32)
        
        # Create playback session
        session = PlaybackSession.objects.create(
            session_token=session_token,
            user=request.user,
            video=video,
            device=device,
            lesson=lesson,
            start_position=start_position,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
        )
        
        # Generate video URLs and DRM tokens
        response_data = {
            'session_token': session_token,
            'session_id': str(session.id),
            'expires_at': (timezone.now() + timezone.timedelta(hours=2)).isoformat(),
            'heartbeat_interval': 30,
        }
        
        # Generate signed URLs or DRM tokens based on video configuration
        if video.vdocipher_video_id:
            # Use VdoCipher DRM
            vdocipher = VdoCipherIntegration()
            drm_response = vdocipher.generate_otp(
                video.vdocipher_video_id,
                str(request.user.id),
                expiration_minutes=120
            )
            response_data['drm_token'] = drm_response
            response_data['video_type'] = 'drm'
            
        else:
            # Use signed URLs for S3/CloudFront
            url_generator = S3SignedURLGenerator()
            streaming_urls = url_generator.generate_streaming_urls(video, 120)
            response_data['video_urls'] = streaming_urls
            response_data['video_type'] = 'signed_url'
        
        # Update video view count
        video.view_count += 1
        video.save(update_fields=['view_count'])
        
        # Create or update lesson progress
        if lesson:
            lesson_progress, created = LessonProgress.objects.get_or_create(
                user=request.user,
                lesson=lesson,
                enrollment=enrollment,
                defaults={'status': 'in_progress'}
            )
            if not created and lesson_progress.status == 'not_started':
                lesson_progress.status = 'in_progress'
                lesson_progress.save(update_fields=['status'])
        
        return Response(response_data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'error': 'Failed to start playback session',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@swagger_auto_schema(
    method='post',
    request_body=PlaybackHeartbeatSerializer,
    responses={
        200: 'Heartbeat recorded',
        400: 'Bad Request',
        404: 'Session not found',
    },
    operation_description='Send playback heartbeat to maintain session'
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def heartbeat(request):
    """Send playback heartbeat to maintain active session"""
    serializer = PlaybackHeartbeatSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    session_token = serializer.validated_data['session_token']
    current_position = serializer.validated_data['current_position']
    buffer_events = serializer.validated_data.get('buffer_events', 0)
    video_quality = serializer.validated_data.get('video_quality', '')
    screen_recording_detected = serializer.validated_data.get('screen_recording_detected', False)
    
    try:
        session = get_object_or_404(
            PlaybackSession,
            session_token=session_token,
            user=request.user
        )
        
        # Check if session is still valid
        if not session.is_active():
            session.status = 'abandoned'
            session.ended_at = timezone.now()
            session.save()
            
            return Response({
                'error': 'Session expired',
                'message': 'Playback session has expired. Please start a new session.'
            }, status=status.HTTP_410_GONE)
        
        # Update session data
        session.current_position = current_position
        session.buffer_events += buffer_events
        session.video_quality = video_quality
        session.last_heartbeat_at = timezone.now()
        session.missed_heartbeats = 0
        
        # Handle screen recording detection
        if screen_recording_detected and not session.screen_recording_detected:
            session.screen_recording_detected = True
            session.status = 'paused'  # Auto-pause on screen recording
            
            # Log security event
            print(f"Screen recording detected for user {request.user.id} in session {session.id}")
        
        # Update watch duration
        if session.status == 'active':
            session.watch_duration += session.heartbeat_interval
        
        session.save()
        
        # Update lesson progress if applicable
        if session.lesson:
            update_lesson_progress(session)
        
        return Response({
            'status': 'heartbeat_recorded',
            'session_status': session.status,
            'should_pause': screen_recording_detected
        }, status=status.HTTP_200_OK)
        
    except PlaybackSession.DoesNotExist:
        return Response({
            'error': 'Session not found',
            'message': 'Invalid session token or session has expired.'
        }, status=status.HTTP_404_NOT_FOUND)

@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'session_token': openapi.Schema(type=openapi.TYPE_STRING),
            'end_position': openapi.Schema(type=openapi.TYPE_INTEGER),
            'completion_percentage': openapi.Schema(type=openapi.TYPE_NUMBER),
        },
        required=['session_token']
    ),
    responses={
        200: 'Playback session ended',
        404: 'Session not found',
    },
    operation_description='End a video playback session'
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def end_playback(request):
    """End a video playback session"""
    session_token = request.data.get('session_token')
    end_position = request.data.get('end_position', 0)
    completion_percentage = request.data.get('completion_percentage', 0.0)
    
    if not session_token:
        return Response({
            'error': 'Session token is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        session = get_object_or_404(
            PlaybackSession,
            session_token=session_token,
            user=request.user
        )
        
        # Update session end data
        session.end_position = end_position
        session.status = 'completed' if completion_percentage >= 80 else 'abandoned'
        session.ended_at = timezone.now()
        session.save()
        
        # Update lesson progress if applicable
        if session.lesson:
            update_lesson_progress(session, completion_percentage)
        
        # Update user profile stats
        profile = request.user.profile
        profile.total_watch_time += session.watch_duration
        profile.save(update_fields=['total_watch_time'])
        
        return Response({
            'message': 'Playback session ended successfully',
            'watch_duration': session.watch_duration,
            'completion_percentage': completion_percentage
        }, status=status.HTTP_200_OK)
        
    except PlaybackSession.DoesNotExist:
        return Response({
            'error': 'Session not found'
        }, status=status.HTTP_404_NOT_FOUND)

@swagger_auto_schema(
    method='get',
    responses={
        200: openapi.Response(
            description='Active sessions',
            schema=openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(type=openapi.TYPE_OBJECT)
            )
        )
    },
    operation_description='Get user active playback sessions'
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def active_sessions(request):
    """Get user's active playback sessions"""
    sessions = PlaybackSession.objects.filter(
        user=request.user,
        status__in=['started', 'active', 'paused']
    ).select_related('video', 'device', 'lesson')
    
    serializer = PlaybackSessionSerializer(sessions, many=True)
    return Response(serializer.data)

# Utility functions

def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def update_lesson_progress(session, completion_percentage=None):
    """Update lesson progress based on playback session"""
    try:
        lesson_progress = LessonProgress.objects.get(
            user=session.user,
            lesson=session.lesson
        )
        
        # Update watch time and position
        lesson_progress.watch_time = session.watch_duration
        lesson_progress.last_position = session.current_position
        lesson_progress.last_accessed_at = timezone.now()
        
        # Calculate completion percentage if not provided
        if completion_percentage is None:
            if session.lesson.duration > 0:
                completion_percentage = (session.current_position / session.lesson.duration) * 100
            else:
                completion_percentage = 0
        
        lesson_progress.completion_percentage = min(completion_percentage, 100)
        
        # Mark as completed if completion is high enough
        if completion_percentage >= 80 and lesson_progress.status != 'completed':
            lesson_progress.status = 'completed'
            lesson_progress.completed_at = timezone.now()
            
            # Update enrollment progress
            enrollment = lesson_progress.enrollment
            enrollment.lessons_completed = LessonProgress.objects.filter(
                enrollment=enrollment,
                status='completed'
            ).count()
            
            total_lessons = enrollment.course.chapters.aggregate(
                total=models.Count('lessons')
            )['total'] or 1
            
            enrollment.progress_percentage = (
                enrollment.lessons_completed / total_lessons
            ) * 100
            
            enrollment.last_accessed_at = timezone.now()
            enrollment.save()
        
        lesson_progress.save()
        
    except LessonProgress.DoesNotExist:
        pass