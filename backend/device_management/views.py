from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from datetime import timedelta
import secrets
import hashlib
from .models import Device, VideoSession, AuditLog
from .serializers import (
    DeviceSerializer, DeviceRegisterSerializer, DeviceTransferSerializer,
    VideoSessionSerializer, VideoStartSerializer, VideoHeartbeatSerializer,
    AuditLogSerializer
)
from courses.models import Lesson
from django.core.cache import cache

def get_client_ip(request):
    """Extract client IP from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def log_audit(user, action, request, metadata=None):
    """Create audit log entry"""
    AuditLog.objects.create(
        user=user,
        action=action,
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        metadata=metadata or {}
    )

class DeviceListView(generics.ListAPIView):
    serializer_class = DeviceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Device.objects.filter(user=self.request.user)

class DeviceRegisterView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = DeviceRegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        device_id = serializer.validated_data['device_id']
        device_name = serializer.validated_data['device_name']
        platform = serializer.validated_data['platform']
        
        # Check if device already exists
        existing_device = Device.objects.filter(
            user=request.user,
            device_id=device_id
        ).first()
        
        if existing_device:
            # Reactivate existing device
            # Deactivate all other devices
            Device.objects.filter(user=request.user).update(is_active=False)
            existing_device.is_active = True
            existing_device.ip_address = get_client_ip(request)
            existing_device.user_agent = request.META.get('HTTP_USER_AGENT', '')
            existing_device.save()
            
            log_audit(request.user, 'device_register', request, {
                'device_id': device_id,
                'device_name': device_name,
                'action': 'reactivated'
            })
            
            return Response({
                'message': 'Device reactivated',
                'device': DeviceSerializer(existing_device).data
            })
        
        # Check if user has active device
        active_device = Device.objects.filter(user=request.user, is_active=True).first()
        
        if active_device:
            return Response({
                'error': 'active_device_exists',
                'message': 'You already have an active device. Please transfer or revoke it first.',
                'active_device': DeviceSerializer(active_device).data
            }, status=status.HTTP_409_CONFLICT)
        
        # Create new device
        device = Device.objects.create(
            user=request.user,
            device_id=device_id,
            device_name=device_name,
            platform=platform,
            is_active=True,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        log_audit(request.user, 'device_register', request, {
            'device_id': device_id,
            'device_name': device_name,
            'platform': platform
        })
        
        return Response({
            'message': 'Device registered successfully',
            'device': DeviceSerializer(device).data
        }, status=status.HTTP_201_CREATED)

class DeviceTransferView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = DeviceTransferSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        new_device_id = serializer.validated_data['new_device_id']
        new_device_name = serializer.validated_data['new_device_name']
        platform = serializer.validated_data['platform']
        
        # Deactivate all existing devices
        old_devices = Device.objects.filter(user=request.user, is_active=True)
        old_device_info = [{'id': str(d.id), 'name': d.device_name} for d in old_devices]
        old_devices.update(is_active=False)
        
        # Check if new device already exists
        device = Device.objects.filter(
            user=request.user,
            device_id=new_device_id
        ).first()
        
        if device:
            device.is_active = True
            device.device_name = new_device_name
            device.ip_address = get_client_ip(request)
            device.user_agent = request.META.get('HTTP_USER_AGENT', '')
            device.save()
        else:
            device = Device.objects.create(
                user=request.user,
                device_id=new_device_id,
                device_name=new_device_name,
                platform=platform,
                is_active=True,
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
        
        log_audit(request.user, 'device_transfer', request, {
            'old_devices': old_device_info,
            'new_device': {'id': new_device_id, 'name': new_device_name}
        })
        
        return Response({
            'message': 'Device transferred successfully',
            'device': DeviceSerializer(device).data
        })

class DeviceRevokeView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def delete(self, request, pk):
        try:
            device = Device.objects.get(id=pk, user=request.user)
            device_info = {'id': str(device.id), 'name': device.device_name}
            device.delete()
            
            log_audit(request.user, 'device_transfer', request, {
                'action': 'revoked',
                'device': device_info
            })
            
            return Response({'message': 'Device revoked successfully'})
        except Device.DoesNotExist:
            return Response(
                {'error': 'Device not found'},
                status=status.HTTP_404_NOT_FOUND
            )

class VideoStartView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = VideoStartSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        lesson_id = serializer.validated_data['lesson_id']
        device_id = serializer.validated_data['device_id']
        
        # Verify lesson exists
        try:
            lesson = Lesson.objects.get(id=lesson_id, is_published=True)
        except Lesson.DoesNotExist:
            return Response(
                {'error': 'Lesson not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verify device is active for this user
        device = Device.objects.filter(
            user=request.user,
            device_id=device_id,
            is_active=True
        ).first()
        
        if not device:
            return Response(
                {'error': 'device_not_active', 'message': 'Device not registered or not active'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check for existing active sessions on other devices
        active_session = VideoSession.objects.filter(
            user=request.user,
            is_active=True,
            expires_at__gt=timezone.now()
        ).exclude(device=device).first()
        
        if active_session:
            return Response({
                'error': 'session_exists',
                'message': 'Video is playing on another device',
                'active_device': active_session.device.device_name
            }, status=status.HTTP_409_CONFLICT)
        
        # Deactivate any old sessions for this user
        VideoSession.objects.filter(
            user=request.user,
            is_active=True
        ).update(is_active=False)
        
        # Generate session token
        session_token = secrets.token_urlsafe(32)
        expires_at = timezone.now() + timedelta(hours=2)
        
        # Create video session
        session = VideoSession.objects.create(
            user=request.user,
            device=device,
            lesson=lesson,
            session_token=session_token,
            expires_at=expires_at,
            is_active=True
        )
        
        # Generate signed URL (basic implementation)
        video_url = self.generate_signed_url(lesson, session_token)
        
        log_audit(request.user, 'video_start', request, {
            'lesson_id': str(lesson_id),
            'lesson_title': lesson.title,
            'session_token': session_token[:10] + '...'
        })
        
        return Response({
            'session_token': session_token,
            'video_url': video_url,
            'expires_at': expires_at.isoformat(),
            'lesson': {
                'id': str(lesson.id),
                'title': lesson.title,
                'duration_minutes': lesson.duration_minutes
            }
        })
    
    def generate_signed_url(self, lesson, session_token):
        """Generate signed URL for video (basic implementation)"""
        # In production, this would integrate with S3/CloudFront/VdoCipher
        # For now, return a demo URL with token
        base_url = lesson.video_url or 'https://example.com/videos'
        return f"{base_url}?token={session_token}&lesson={lesson.id}"

class VideoHeartbeatView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = VideoHeartbeatSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        session_token = serializer.validated_data['session_token']
        current_time = serializer.validated_data['current_time']
        
        # Find session
        try:
            session = VideoSession.objects.get(
                session_token=session_token,
                user=request.user,
                is_active=True
            )
        except VideoSession.DoesNotExist:
            return Response(
                {'error': 'Invalid or expired session'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if session expired
        if timezone.now() > session.expires_at:
            session.is_active = False
            session.save()
            return Response(
                {'error': 'Session expired'},
                status=status.HTTP_410_GONE
            )
        
        # Update heartbeat and watch time
        session.watch_time_seconds = current_time
        session.save(update_fields=['last_heartbeat', 'watch_time_seconds'])
        
        # Cache the heartbeat to detect multiple devices
        cache_key = f'video_session_{session.id}'
        cache.set(cache_key, timezone.now().isoformat(), timeout=30)
        
        return Response({
            'status': 'ok',
            'expires_in': int((session.expires_at - timezone.now()).total_seconds())
        })

class VideoEndView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        session_token = request.data.get('session_token')
        final_time = request.data.get('final_time', 0)
        
        try:
            session = VideoSession.objects.get(
                session_token=session_token,
                user=request.user
            )
            
            session.is_active = False
            session.watch_time_seconds = final_time
            session.save()
            
            log_audit(request.user, 'video_end', request, {
                'lesson_id': str(session.lesson.id),
                'watch_time': final_time,
                'duration': session.lesson.duration_minutes * 60
            })
            
            return Response({'message': 'Session ended successfully'})
        except VideoSession.DoesNotExist:
            return Response(
                {'error': 'Session not found'},
                status=status.HTTP_404_NOT_FOUND
            )

class AuditLogListView(generics.ListAPIView):
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.role == 'admin':
            return AuditLog.objects.all()
        return AuditLog.objects.filter(user=self.request.user)
