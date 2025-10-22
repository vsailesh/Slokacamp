from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User, UserProfile
import requests
from django.conf import settings

class UserRegistrationSerializer(serializers.ModelSerializer):
    """User registration with email verification"""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)
    device_id = serializers.CharField(write_only=True)
    device_name = serializers.CharField(write_only=True)
    platform = serializers.ChoiceField(choices=['ios', 'android'], write_only=True)
    push_token = serializers.CharField(required=False, allow_blank=True, write_only=True)
    
    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name', 'password', 
                 'confirm_password', 'device_id', 'device_name', 'platform', 'push_token']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        # Remove device and password confirmation data
        device_data = {
            'device_id': validated_data.pop('device_id'),
            'device_name': validated_data.pop('device_name'),
            'platform': validated_data.pop('platform'),
            'push_token': validated_data.pop('push_token', '')
        }
        validated_data.pop('confirm_password')
        
        # Create user
        user = User.objects.create_user(**validated_data)
        
        # Create user profile
        UserProfile.objects.create(user=user)
        
        # Register device
        from devices.models import Device
        Device.objects.create(
            user=user,
            is_primary=True,
            **device_data
        )
        
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom JWT token serializer with device information"""
    device_id = serializers.CharField()
    device_name = serializers.CharField(required=False)
    platform = serializers.ChoiceField(choices=['ios', 'android', 'web'], required=False)
    push_token = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Handle device registration/update
        from devices.models import Device
        from django.conf import settings
        
        device_id = attrs.get('device_id')
        user = self.user
        
        try:
            device = Device.objects.get(device_id=device_id, user=user)
            # Update existing device
            device.last_seen_at = timezone.now()
            if attrs.get('push_token'):
                device.push_token = attrs.get('push_token')
                device.push_token_updated_at = timezone.now()
            device.save()
            
        except Device.DoesNotExist:
            # Handle new device registration based on policy
            device_policy = getattr(settings, 'DEVICE_POLICY', 'deactivate_previous')
            max_devices = getattr(settings, 'MAX_DEVICES_PER_USER', 1)
            
            active_devices = Device.objects.filter(user=user, is_active=True).count()
            
            if active_devices >= max_devices:
                if device_policy == 'block_new':
                    raise serializers.ValidationError(
                        "Maximum number of devices reached. Please deactivate another device first."
                    )
                elif device_policy == 'deactivate_previous':
                    # Deactivate oldest device
                    oldest_device = Device.objects.filter(
                        user=user, is_active=True
                    ).order_by('last_seen_at').first()
                    if oldest_device:
                        oldest_device.deactivate()
            
            # Create new device
            device = Device.objects.create(
                user=user,
                device_id=device_id,
                device_name=attrs.get('device_name', f"{attrs.get('platform', 'Unknown')} Device"),
                platform=attrs.get('platform', 'unknown'),
                push_token=attrs.get('push_token', ''),
                is_primary=True,
                is_active=True
            )
        
        # Add device info to token response
        data['device_id'] = device.id
        data['is_primary_device'] = device.is_primary
        
        return data

class SocialAuthSerializer(serializers.Serializer):
    """Social authentication serializer"""
    provider = serializers.ChoiceField(choices=['google', 'facebook', 'apple'])
    access_token = serializers.CharField()
    device_id = serializers.CharField()
    device_name = serializers.CharField()
    platform = serializers.ChoiceField(choices=['ios', 'android'])
    push_token = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, attrs):
        provider = attrs.get('provider')
        access_token = attrs.get('access_token')
        
        # Validate token with respective provider
        user_data = None
        
        if provider == 'google':
            user_data = self._validate_google_token(access_token)
        elif provider == 'facebook':
            user_data = self._validate_facebook_token(access_token)
        elif provider == 'apple':
            user_data = self._validate_apple_token(access_token)
        
        if not user_data:
            raise serializers.ValidationError("Invalid social auth token")
        
        attrs['user_data'] = user_data
        return attrs
    
    def _validate_google_token(self, token):
        """Validate Google OAuth token"""
        try:
            response = requests.get(
                f'https://www.googleapis.com/oauth2/v1/userinfo?access_token={token}'
            )
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return None
    
    def _validate_facebook_token(self, token):
        """Validate Facebook token"""
        try:
            response = requests.get(
                f'https://graph.facebook.com/me?fields=id,email,first_name,last_name,picture&access_token={token}'
            )
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return None
    
    def _validate_apple_token(self, token):
        """Validate Apple Sign In token"""
        # Apple Sign In uses JWT tokens that need to be validated
        # This is a simplified version - in production, you'd validate the JWT
        try:
            import jwt
            # You'd need to fetch Apple's public keys and validate the JWT
            # This is a placeholder for the actual implementation
            decoded = jwt.decode(token, options={"verify_signature": False})
            return {
                'id': decoded.get('sub'),
                'email': decoded.get('email'),
                'first_name': '',
                'last_name': ''
            }
        except:
            pass
        return None
    
    def create_or_update_user(self, validated_data):
        """Create or update user from social auth data"""
        user_data = validated_data['user_data']
        provider = validated_data['provider']
        
        # Look for existing user
        user = None
        email = user_data.get('email')
        provider_id = user_data.get('id')
        
        if email:
            user = User.objects.filter(email=email).first()
        
        if not user and provider_id:
            # Look for user by provider ID
            if provider == 'google':
                user = User.objects.filter(google_id=provider_id).first()
            elif provider == 'facebook':
                user = User.objects.filter(facebook_id=provider_id).first()
            elif provider == 'apple':
                user = User.objects.filter(apple_id=provider_id).first()
        
        if not user:
            # Create new user
            user = User.objects.create_user(
                username=email or f"{provider}_{provider_id}",
                email=email or '',
                first_name=user_data.get('first_name', ''),
                last_name=user_data.get('last_name', ''),
                email_verified=True if email else False
            )
            UserProfile.objects.create(user=user)
        
        # Update provider ID
        if provider == 'google':
            user.google_id = provider_id
        elif provider == 'facebook':
            user.facebook_id = provider_id
        elif provider == 'apple':
            user.apple_id = provider_id
        
        user.save()
        
        # Register/update device
        from devices.models import Device
        device, created = Device.objects.get_or_create(
            user=user,
            device_id=validated_data['device_id'],
            defaults={
                'device_name': validated_data['device_name'],
                'platform': validated_data['platform'],
                'push_token': validated_data.get('push_token', ''),
                'is_primary': True
            }
        )
        
        if not created:
            device.make_primary()
        
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    """User profile serializer"""
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    is_subscription_active = serializers.BooleanField(source='user.is_subscription_active', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ['full_name', 'email', 'is_subscription_active', 'dosha_type', 
                 'learning_goals', 'experience_level', 'health_conditions', 
                 'dietary_preferences', 'total_watch_time', 'courses_completed', 
                 'streak_days', 'email_notifications', 'push_notifications', 
                 'weekly_digest']
        read_only_fields = ['total_watch_time', 'courses_completed', 'streak_days']

class PasswordResetSerializer(serializers.Serializer):
    """Password reset request serializer"""
    email = serializers.EmailField()
    
    def validate_email(self, value):
        if not User.objects.filter(email=value, is_active=True).exists():
            raise serializers.ValidationError("No active user found with this email address.")
        return value

class PasswordResetConfirmSerializer(serializers.Serializer):
    """Password reset confirmation serializer"""
    token = serializers.CharField()
    new_password = serializers.CharField(validators=[validate_password])
    confirm_password = serializers.CharField()
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs