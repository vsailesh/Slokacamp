from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from .models import SubscriptionPlan, Subscription, Payment
from .serializers import (
    SubscriptionPlanSerializer, SubscriptionSerializer,
    PaymentSerializer, CreateCheckoutSessionSerializer
)
from .stripe_service import StripeService
from device_management.models import AuditLog

class SubscriptionPlanListView(generics.ListAPIView):
    """List all available subscription plans"""
    queryset = SubscriptionPlan.objects.filter(is_active=True)
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [permissions.AllowAny]

class MySubscriptionView(APIView):
    """Get current user's subscription"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        try:
            subscription = Subscription.objects.get(user=request.user)
            serializer = SubscriptionSerializer(subscription)
            return Response(serializer.data)
        except Subscription.DoesNotExist:
            return Response(
                {'message': 'No active subscription'},
                status=status.HTTP_404_NOT_FOUND
            )

class CreateCheckoutSessionView(APIView):
    """Create Stripe checkout session"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = CreateCheckoutSessionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        plan_id = serializer.validated_data['plan_id']
        success_url = serializer.validated_data['success_url']
        cancel_url = serializer.validated_data['cancel_url']
        
        try:
            plan = SubscriptionPlan.objects.get(id=plan_id, is_active=True)
        except SubscriptionPlan.DoesNotExist:
            return Response(
                {'error': 'Plan not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if user already has active subscription
        if hasattr(request.user, 'subscription'):
            if request.user.subscription.is_valid():
                return Response(
                    {'error': 'You already have an active subscription'},
                    status=status.HTTP_409_CONFLICT
                )
        
        try:
            checkout_session = StripeService.create_checkout_session(
                request.user, plan, success_url, cancel_url
            )
            
            return Response({
                'checkout_url': checkout_session.url,
                'session_id': checkout_session.id
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CancelSubscriptionView(APIView):
    """Cancel subscription at period end"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            subscription = Subscription.objects.get(user=request.user)
        except Subscription.DoesNotExist:
            return Response(
                {'error': 'No active subscription'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if subscription.status not in ['active', 'trialing']:
            return Response(
                {'error': 'Subscription is not active'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            StripeService.cancel_subscription(subscription)
            
            AuditLog.objects.create(
                user=request.user,
                action='subscription_end',
                ip_address=request.META.get('REMOTE_ADDR'),
                metadata={'reason': 'user_canceled'}
            )
            
            return Response({
                'message': 'Subscription will be canceled at period end',
                'period_end': subscription.current_period_end
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ReactivateSubscriptionView(APIView):
    """Reactivate a canceled subscription"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            subscription = Subscription.objects.get(user=request.user)
        except Subscription.DoesNotExist:
            return Response(
                {'error': 'No subscription found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if subscription.auto_renew:
            return Response(
                {'error': 'Subscription is already active'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            StripeService.reactivate_subscription(subscription)
            
            return Response({
                'message': 'Subscription reactivated successfully'
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class PaymentHistoryView(generics.ListAPIView):
    """List user's payment history"""
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)

@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(APIView):
    """Handle Stripe webhook events"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        
        try:
            event = StripeService.handle_webhook_event(payload, sig_header)
            return HttpResponse(status=200)
        except Exception as e:
            return HttpResponse(str(e), status=400)
