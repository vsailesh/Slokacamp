# Authentication Views for Django REST API
# Handles user registration, login, social auth, and device management

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.utils.crypto import get_random_string
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import User, UserProfile
from .serializers import (
    UserRegistrationSerializer,
    CustomTokenObtainPairSerializer,
    SocialAuthSerializer,
    UserProfileSerializer,
    PasswordResetSerializer,
    PasswordResetConfirmSerializer
)
from devices.models import Device
from devices.serializers import DeviceSerializer

@swagger_auto_schema(
    method='post',
    request_body=UserRegistrationSerializer,
    responses={
        201: openapi.Response(
            description='User created successfully',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'user_id': openapi.Schema(type=openapi.TYPE_STRING),
                    'device_id': openapi.Schema(type=openapi.TYPE_STRING),
                }
            )
        ),
        400: 'Bad Request - Validation errors',
    },
    operation_description='Register a new user account with device registration'
)
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """Register a new user account with automatic device registration"""
    serializer = UserRegistrationSerializer(data=request.data)
    
    if serializer.is_valid():
        try:
            user = serializer.save()
            
            # Send verification email
            verification_token = get_random_string(32)
            user.email_verification_token = verification_token
            user.save()
            
            # Send verification email
            send_verification_email(user, verification_token)
            
            # Get the registered device
            device = user.devices.filter(is_primary=True).first()
            
            return Response({
                'message': 'User registered successfully. Please check your email for verification.',
                'user_id': str(user.id),
                'device_id': str(device.id) if device else None,
                'email_verification_required': True
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'error': 'Registration failed',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='post',
    request_body=CustomTokenObtainPairSerializer,
    responses={
        200: openapi.Response(
            description='Login successful',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'access': openapi.Schema(type=openapi.TYPE_STRING),
                    'refresh': openapi.Schema(type=openapi.TYPE_STRING),
                    'device_id': openapi.Schema(type=openapi.TYPE_STRING),
                    'is_primary_device': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'user': openapi.Schema(type=openapi.TYPE_OBJECT),
                }
            )
        ),
        400: 'Bad Request - Invalid credentials',
        403: 'Forbidden - Device limit reached',
    },
    operation_description='User login with device registration/validation'
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """User login with automatic device management"""
    serializer = CustomTokenObtainPairSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.user
        
        # Check if user email is verified
        if not user.email_verified:
            return Response({
                'error': 'Email not verified',
                'message': 'Please verify your email address before logging in.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get tokens and device info from serializer
        tokens = serializer.validated_data
        
        # Update user last login
        user.last_login = timezone.now()
        user.last_active = timezone.now()
        user.save(update_fields=['last_login', 'last_active'])
        
        # Get user profile
        profile_serializer = UserProfileSerializer(user.profile)
        
        return Response({
            'access': tokens['access'],
            'refresh': tokens['refresh'],
            'device_id': tokens['device_id'],
            'is_primary_device': tokens['is_primary_device'],
            'user': {
                'id': str(user.id),
                'email': user.email,
                'full_name': user.full_name,
                'profile': profile_serializer.data,
            }
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='post',
    request_body=SocialAuthSerializer,
    responses={
        200: 'Social authentication successful',
        400: 'Bad Request - Invalid token or data',
    },
    operation_description='Social authentication (Google, Facebook, Apple)'
)
@api_view(['POST'])
@permission_classes([AllowAny])
def social_auth(request):
    """Social authentication with Google, Facebook, or Apple"""
    serializer = SocialAuthSerializer(data=request.data)
    
    if serializer.is_valid():
        try:
            user = serializer.create_or_update_user(serializer.validated_data)
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            
            # Get user's primary device
            device = user.devices.filter(is_primary=True, is_active=True).first()
            
            # Get user profile
            profile_serializer = UserProfileSerializer(user.profile)
            
            return Response({
                'access': str(access_token),
                'refresh': str(refresh),
                'device_id': str(device.id) if device else None,
                'is_primary_device': device.is_primary if device else False,
                'user': {
                    'id': str(user.id),
                    'email': user.email,
                    'full_name': user.full_name,
                    'profile': profile_serializer.data,
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': 'Social authentication failed',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='Refresh token'),
        },
        required=['refresh']
    ),
    responses={
        200: 'Token refreshed successfully',
        400: 'Bad Request - Invalid refresh token',
    },
    operation_description='Refresh JWT access token'
)
@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):
    """Refresh JWT access token"""
    try:
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({
                'error': 'Refresh token is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        refresh = RefreshToken(refresh_token)
        access_token = refresh.access_token
        
        return Response({
            'access': str(access_token),
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': 'Invalid refresh token',
            'details': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='get',
    responses={
        200: UserProfileSerializer,
    },
    operation_description='Get current user profile'
)
@swagger_auto_schema(
    method='patch',
    request_body=UserProfileSerializer,
    responses={
        200: UserProfileSerializer,
    },
    operation_description='Update current user profile'
)
@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """Get or update current user profile"""
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    if request.method == 'GET':
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)
    
    elif request.method == 'PATCH':
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='post',
    request_body=PasswordResetSerializer,
    responses={
        200: 'Password reset email sent',
        400: 'Bad Request - Invalid email',
    },
    operation_description='Request password reset'
)
@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset(request):
    """Request password reset email"""
    serializer = PasswordResetSerializer(data=request.data)
    
    if serializer.is_valid():
        email = serializer.validated_data['email']
        
        try:
            user = User.objects.get(email=email, is_active=True)
            
            # Generate reset token
            reset_token = get_random_string(64)
            user.password_reset_token = reset_token
            user.password_reset_token_expires = timezone.now() + timezone.timedelta(hours=1)
            user.save()
            
            # Send password reset email
            send_password_reset_email(user, reset_token)
            
            return Response({
                'message': 'Password reset email sent successfully'
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            # Don't reveal whether email exists or not
            return Response({
                'message': 'If the email exists, a password reset link has been sent'
            }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='post',
    request_body=PasswordResetConfirmSerializer,
    responses={
        200: 'Password reset successful',
        400: 'Bad Request - Invalid token or password',
    },
    operation_description='Confirm password reset'
)
@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_confirm(request):
    """Confirm password reset with token"""
    serializer = PasswordResetConfirmSerializer(data=request.data)
    
    if serializer.is_valid():
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']
        
        try:
            user = User.objects.get(
                password_reset_token=token,
                password_reset_token_expires__gt=timezone.now()
            )
            
            # Reset password
            user.set_password(new_password)
            user.password_reset_token = None
            user.password_reset_token_expires = None
            user.save()
            
            return Response({
                'message': 'Password reset successful'
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response({
                'error': 'Invalid or expired reset token'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'token': openapi.Schema(type=openapi.TYPE_STRING, description='Verification token'),
        },
        required=['token']
    ),
    responses={
        200: 'Email verified successfully',
        400: 'Bad Request - Invalid token',
    },
    operation_description='Verify user email address'
)
@api_view(['POST'])
@permission_classes([AllowAny])
def verify_email(request):
    """Verify user email address"""
    token = request.data.get('token')
    
    if not token:
        return Response({
            'error': 'Verification token is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(email_verification_token=token)
        
        if user.email_verified:
            return Response({
                'message': 'Email already verified'
            }, status=status.HTTP_200_OK)
        
        user.email_verified = True
        user.email_verification_token = None
        user.save()
        
        return Response({
            'message': 'Email verified successfully'
        }, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        return Response({
            'error': 'Invalid verification token'
        }, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='post',
    responses={
        200: 'Logout successful',
    },
    operation_description='User logout'
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """User logout - blacklist refresh token"""
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        
        # Update user last activity
        request.user.last_active = timezone.now()
        request.user.save(update_fields=['last_active'])
        
        return Response({
            'message': 'Logout successful'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'message': 'Logout successful'
        }, status=status.HTTP_200_OK)  # Always return success for logout

# Utility functions

def send_verification_email(user, token):
    """Send email verification email"""
    verification_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
    
    subject = 'Verify your SlokaCamp account'
    message = f"""
Welcome to SlokaCamp!

Please verify your email address by clicking the link below:
{verification_url}

This link will expire in 24 hours.

If you didn't create an account with SlokaCamp, please ignore this email.

Best regards,
The SlokaCamp Team
"""
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
    except Exception as e:
        print(f"Failed to send verification email: {e}")

def send_password_reset_email(user, token):
    """Send password reset email"""
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    
    subject = 'Reset your SlokaCamp password'
    message = f"""
Hi {user.first_name or user.username},

You requested a password reset for your SlokaCamp account.

Click the link below to reset your password:
{reset_url}

This link will expire in 1 hour.

If you didn't request this reset, please ignore this email.

Best regards,
The SlokaCamp Team
"""
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
    except Exception as e:
        print(f"Failed to send password reset email: {e}")