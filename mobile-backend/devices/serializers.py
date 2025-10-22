from rest_framework import serializers
from .models import Device, DeviceTransfer
from django.utils import timezone
from django.conf import settings

class DeviceSerializer(serializers.ModelSerializer):
    """Device serializer for API responses"""
    is_online = serializers.ReadOnlyField()
    
    class Meta:
        model = Device
        fields = [
            'id', 'device_id', 'device_name', 'platform', 'os_version', 
            'app_version', 'device_model', 'is_active', 'is_primary',
            'is_online', 'registered_at', 'last_seen_at'
        ]
        read_only_fields = ['id', 'registered_at', 'last_seen_at', 'is_online']

class DeviceRegistrationSerializer(serializers.ModelSerializer):
    """Device registration serializer"""
    
    class Meta:
        model = Device
        fields = [
            'device_id', 'device_name', 'platform', 'os_version',
            'app_version', 'device_model', 'push_token', 'device_fingerprint'
        ]
    
    def create(self, validated_data):
        user = self.context['request'].user
        
        # Check device policy
        device_policy = getattr(settings, 'DEVICE_POLICY', 'deactivate_previous')
        max_devices = getattr(settings, 'MAX_DEVICES_PER_USER', 1)
        
        active_devices_count = Device.objects.filter(
            user=user, 
            is_active=True
        ).count()
        
        if active_devices_count >= max_devices:
            if device_policy == 'block_new':
                raise serializers.ValidationError(
                    "Maximum number of devices reached. Please deactivate another device first."
                )
            elif device_policy == 'deactivate_previous':
                # Deactivate oldest device
                oldest_device = Device.objects.filter(
                    user=user, 
                    is_active=True
                ).order_by('last_seen_at').first()
                
                if oldest_device:
                    oldest_device.deactivate()
        
        # Create new device
        device = Device.objects.create(
            user=user,
            is_primary=True,
            is_active=True,
            **validated_data
        )
        
        return device

class DeviceTransferSerializer(serializers.Serializer):
    """Device transfer request serializer"""
    new_device_id = serializers.CharField(max_length=255)
    device_name = serializers.CharField(max_length=255)
    platform = serializers.ChoiceField(choices=['ios', 'android', 'web'])
    reason = serializers.ChoiceField(
        choices=['manual_transfer', 'device_lost', 'policy_enforcement'],
        default='manual_transfer'
    )
    
    def validate_new_device_id(self, value):
        user = self.context['request'].user
        
        # Check if device already exists
        if Device.objects.filter(device_id=value, user=user).exists():
            raise serializers.ValidationError(
                "Device already registered for this user"
            )
        
        return value
    
    def create(self, validated_data):
        user = self.context['request'].user
        request = self.context['request']
        
        # Get current primary device
        old_device = Device.objects.filter(
            user=user, 
            is_primary=True, 
            is_active=True
        ).first()
        
        # Create new device
        new_device = Device.objects.create(
            user=user,
            device_id=validated_data['new_device_id'],
            device_name=validated_data['device_name'],
            platform=validated_data['platform'],
            is_primary=True,
            is_active=True,
            last_ip_address=self.get_client_ip(request)
        )
        
        # Create transfer record
        transfer = DeviceTransfer.objects.create(
            user=user,
            from_device=old_device,
            to_device=new_device,
            reason=validated_data['reason'],
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
        )
        
        # Deactivate old device
        if old_device:
            old_device.deactivate()
        
        return {
            'transfer': transfer,
            'device': new_device
        }
    
    def get_client_ip(self, request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class DeviceTransferResponseSerializer(serializers.ModelSerializer):
    """Device transfer response serializer"""
    device = DeviceSerializer(source='to_device', read_only=True)
    
    class Meta:
        model = DeviceTransfer
        fields = ['id', 'reason', 'created_at', 'device']
        read_only_fields = ['id', 'created_at']