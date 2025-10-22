from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Device, DeviceTransfer
from .serializers import (
    DeviceSerializer,
    DeviceRegistrationSerializer,
    DeviceTransferSerializer,
    DeviceTransferResponseSerializer
)

@swagger_auto_schema(
    method='get',
    responses={200: DeviceSerializer(many=True)},
    operation_description='List all devices registered for the current user'
)
@swagger_auto_schema(
    method='post',
    request_body=DeviceRegistrationSerializer,
    responses={
        201: DeviceSerializer,
        400: 'Bad Request - Validation errors',
        409: 'Conflict - Device limit reached'
    },
    operation_description='Register a new device for the current user'
)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def device_list(request):
    """List user devices or register a new device"""
    
    if request.method == 'GET':
        devices = Device.objects.filter(user=request.user).order_by('-last_seen_at')
        serializer = DeviceSerializer(devices, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = DeviceRegistrationSerializer(
            data=request.data, 
            context={'request': request}
        )
        
        if serializer.is_valid():
            try:
                device = serializer.save()
                response_serializer = DeviceSerializer(device)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({
                    'error': 'Device registration failed',
                    'details': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='get',
    responses={200: DeviceSerializer},
    operation_description='Get device details'
)
@swagger_auto_schema(
    method='patch',
    request_body=DeviceSerializer,
    responses={200: DeviceSerializer},
    operation_description='Update device information'
)
@swagger_auto_schema(
    method='delete',
    responses={204: 'Device deactivated'},
    operation_description='Deactivate a device'
)
@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def device_detail(request, device_id):
    """Get, update, or deactivate a specific device"""
    device = get_object_or_404(
        Device, 
        id=device_id, 
        user=request.user
    )
    
    if request.method == 'GET':
        serializer = DeviceSerializer(device)
        return Response(serializer.data)
    
    elif request.method == 'PATCH':
        serializer = DeviceSerializer(
            device, 
            data=request.data, 
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        device.deactivate()
        return Response(status=status.HTTP_204_NO_CONTENT)

@swagger_auto_schema(
    method='post',
    request_body=DeviceTransferSerializer,
    responses={
        200: DeviceTransferResponseSerializer,
        400: 'Bad Request - Validation errors'
    },
    operation_description='Transfer device access to a new device'
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def device_transfer(request):
    """Transfer device access to a new device"""
    serializer = DeviceTransferSerializer(
        data=request.data,
        context={'request': request}
    )
    
    if serializer.is_valid():
        try:
            result = serializer.save()
            response_serializer = DeviceTransferResponseSerializer(result['transfer'])
            
            return Response({
                'message': 'Device transfer completed successfully',
                'transfer': response_serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': 'Device transfer failed',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='post',
    responses={200: 'Heartbeat recorded'},
    operation_description='Update device heartbeat (last seen timestamp)'
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def device_heartbeat(request, device_id):
    """Update device heartbeat to indicate it's active"""
    device = get_object_or_404(
        Device,
        id=device_id,
        user=request.user,
        is_active=True
    )
    
    # Update last seen timestamp
    device.last_seen_at = timezone.now()
    device.save(update_fields=['last_seen_at'])
    
    return Response({
        'message': 'Heartbeat recorded',
        'last_seen_at': device.last_seen_at
    })

@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'device_id': openapi.Schema(type=openapi.TYPE_STRING)
        },
        required=['device_id']
    ),
    responses={
        200: DeviceSerializer,
        404: 'Device not found'
    },
    operation_description='Make a device the primary device for the user'
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def set_primary_device(request):
    """Set a device as the primary device for the user"""
    device_id = request.data.get('device_id')
    
    if not device_id:
        return Response({
            'error': 'device_id is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    device = get_object_or_404(
        Device,
        device_id=device_id,
        user=request.user,
        is_active=True
    )
    
    # Make this device primary
    device.make_primary()
    
    serializer = DeviceSerializer(device)
    return Response({
        'message': 'Primary device updated successfully',
        'device': serializer.data
    })

@swagger_auto_schema(
    method='get',
    responses={
        200: openapi.Response(
            description='Device transfer history',
            schema=openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(type=openapi.TYPE_OBJECT)
            )
        )
    },
    operation_description='Get device transfer history for the current user'
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def device_transfer_history(request):
    """Get device transfer history for the current user"""
    transfers = DeviceTransfer.objects.filter(
        user=request.user
    ).select_related('from_device', 'to_device').order_by('-created_at')
    
    serializer = DeviceTransferResponseSerializer(transfers, many=True)
    return Response(serializer.data)