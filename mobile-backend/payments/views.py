# Payment and Subscription Views
# Handles Stripe integration, subscription management, and payment processing

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import stripe
import json
from django.utils import timezone

from .models import Subscription, SubscriptionPlan, Payment, RefundRequest
from .serializers import (
    SubscriptionPlanSerializer,
    SubscriptionSerializer,
    PaymentSerializer,
    SubscriptionCreateSerializer,
    RefundRequestSerializer
)

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

@swagger_auto_schema(
    method='get',
    responses={200: SubscriptionPlanSerializer(many=True)},
    operation_description='Get all available subscription plans'
)
@api_view(['GET'])
@permission_classes([AllowAny])
def subscription_plans(request):
    """Get all available subscription plans"""
    plans = SubscriptionPlan.objects.filter(is_active=True).order_by('price')
    serializer = SubscriptionPlanSerializer(plans, many=True)
    return Response(serializer.data)

@swagger_auto_schema(
    method='post',
    request_body=SubscriptionCreateSerializer,
    responses={
        201: 'Subscription created successfully',
        400: 'Bad Request - Invalid data',
        402: 'Payment Required - Payment failed'
    },
    operation_description='Create a new subscription'
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_subscription(request):
    """Create a new subscription for the user"""
    serializer = SubscriptionCreateSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    plan_id = serializer.validated_data['plan_id']
    payment_method_id = serializer.validated_data['payment_method_id']
    
    try:
        # Get subscription plan
        plan = SubscriptionPlan.objects.get(id=plan_id, is_active=True)
        
        # Check if user already has an active subscription
        existing_subscription = Subscription.objects.filter(
            user=request.user,
            status__in=['active', 'trialing']
        ).first()
        
        if existing_subscription:
            return Response({
                'error': 'Active subscription already exists',
                'message': 'Please cancel your current subscription before creating a new one.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create or get Stripe customer
        customer = create_or_get_stripe_customer(request.user)
        
        # Attach payment method to customer
        stripe.PaymentMethod.attach(
            payment_method_id,
            customer=customer.id
        )
        
        # Set as default payment method
        stripe.Customer.modify(
            customer.id,
            invoice_settings={'default_payment_method': payment_method_id}
        )
        
        # Create Stripe subscription
        stripe_subscription = stripe.Subscription.create(
            customer=customer.id,
            items=[{
                'price': plan.stripe_price_id,
            }],
            payment_behavior='default_incomplete',
            payment_settings={'save_default_payment_method': 'on_subscription'},
            expand=['latest_invoice.payment_intent'],
            trial_period_days=plan.trial_period_days if plan.trial_period_days > 0 else None,
            metadata={
                'user_id': str(request.user.id),
                'plan_name': plan.name
            }
        )
        
        # Create local subscription record
        subscription = Subscription.objects.create(
            user=request.user,
            plan_type=plan.billing_period,
            stripe_subscription_id=stripe_subscription.id,
            stripe_customer_id=customer.id,
            stripe_payment_method_id=payment_method_id,
            status=stripe_subscription.status,
            amount=plan.price,
            currency=plan.currency,
            current_period_start=timezone.datetime.fromtimestamp(
                stripe_subscription.current_period_start
            ),
            current_period_end=timezone.datetime.fromtimestamp(
                stripe_subscription.current_period_end
            )
        )
        
        # Handle trial period
        if stripe_subscription.trial_start and stripe_subscription.trial_end:
            subscription.trial_start = timezone.datetime.fromtimestamp(
                stripe_subscription.trial_start
            )
            subscription.trial_end = timezone.datetime.fromtimestamp(
                stripe_subscription.trial_end
            )
            subscription.save()
        
        response_data = {
            'subscription_id': str(subscription.id),
            'stripe_subscription_id': stripe_subscription.id,
            'status': stripe_subscription.status,
        }
        
        # Include client secret if payment confirmation needed
        if stripe_subscription.latest_invoice.payment_intent:
            response_data['client_secret'] = stripe_subscription.latest_invoice.payment_intent.client_secret
        
        return Response(response_data, status=status.HTTP_201_CREATED)
        
    except SubscriptionPlan.DoesNotExist:
        return Response({
            'error': 'Invalid subscription plan'
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except stripe.error.CardError as e:
        return Response({
            'error': 'Payment failed',
            'message': e.user_message
        }, status=status.HTTP_402_PAYMENT_REQUIRED)
        
    except Exception as e:
        return Response({
            'error': 'Subscription creation failed',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@swagger_auto_schema(
    method='get',
    responses={200: SubscriptionSerializer},
    operation_description='Get current user subscription'
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_subscription(request):
    """Get current user's subscription details"""
    try:
        subscription = Subscription.objects.get(
            user=request.user,
            status__in=['active', 'trialing', 'past_due']
        )
        serializer = SubscriptionSerializer(subscription)
        return Response(serializer.data)
        
    except Subscription.DoesNotExist:
        return Response({
            'subscription': None,
            'is_subscribed': False
        })

@swagger_auto_schema(
    method='post',
    responses={200: 'Subscription cancelled'},
    operation_description='Cancel current subscription'
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_subscription(request):
    """Cancel user's current subscription"""
    try:
        subscription = Subscription.objects.get(
            user=request.user,
            status__in=['active', 'trialing']
        )
        
        # Cancel at period end in Stripe
        stripe.Subscription.modify(
            subscription.stripe_subscription_id,
            cancel_at_period_end=True
        )
        
        # Update local record
        subscription.cancel_at_period_end = True
        subscription.canceled_at = timezone.now()
        subscription.save()
        
        return Response({
            'message': 'Subscription will be canceled at the end of the current billing period',
            'cancel_at_period_end': True,
            'current_period_end': subscription.current_period_end
        })
        
    except Subscription.DoesNotExist:
        return Response({
            'error': 'No active subscription found'
        }, status=status.HTTP_404_NOT_FOUND)
        
    except Exception as e:
        return Response({
            'error': 'Cancellation failed',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@swagger_auto_schema(
    method='post',
    responses={200: 'Subscription reactivated'},
    operation_description='Reactivate cancelled subscription'
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reactivate_subscription(request):
    """Reactivate a cancelled subscription"""
    try:
        subscription = Subscription.objects.get(
            user=request.user,
            cancel_at_period_end=True,
            status__in=['active', 'trialing']
        )
        
        # Reactivate in Stripe
        stripe.Subscription.modify(
            subscription.stripe_subscription_id,
            cancel_at_period_end=False
        )
        
        # Update local record
        subscription.cancel_at_period_end = False
        subscription.canceled_at = None
        subscription.save()
        
        return Response({
            'message': 'Subscription reactivated successfully',
            'cancel_at_period_end': False
        })
        
    except Subscription.DoesNotExist:
        return Response({
            'error': 'No cancelled subscription found'
        }, status=status.HTTP_404_NOT_FOUND)

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def stripe_webhook(request):
    """Handle Stripe webhook events"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)
    
    # Handle the event
    if event['type'] == 'invoice.payment_succeeded':
        handle_payment_succeeded(event['data']['object'])
    elif event['type'] == 'invoice.payment_failed':
        handle_payment_failed(event['data']['object'])
    elif event['type'] == 'customer.subscription.updated':
        handle_subscription_updated(event['data']['object'])
    elif event['type'] == 'customer.subscription.deleted':
        handle_subscription_deleted(event['data']['object'])
    
    return HttpResponse(status=200)

@swagger_auto_schema(
    method='get',
    responses={200: PaymentSerializer(many=True)},
    operation_description='Get user payment history'
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def payment_history(request):
    """Get user's payment history"""
    payments = Payment.objects.filter(user=request.user).order_by('-created_at')
    serializer = PaymentSerializer(payments, many=True)
    return Response(serializer.data)

@swagger_auto_schema(
    method='post',
    request_body=RefundRequestSerializer,
    responses={201: RefundRequestSerializer},
    operation_description='Request a refund'
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def request_refund(request):
    """Request a refund for a payment"""
    serializer = RefundRequestSerializer(
        data=request.data,
        context={'request': request}
    )
    
    if serializer.is_valid():
        refund_request = serializer.save()
        return Response(
            RefundRequestSerializer(refund_request).data,
            status=status.HTTP_201_CREATED
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Utility functions

def create_or_get_stripe_customer(user):
    """Create or get existing Stripe customer"""
    try:
        # Try to get existing subscription with customer ID
        subscription = Subscription.objects.filter(
            user=user,
            stripe_customer_id__isnull=False
        ).first()
        
        if subscription and subscription.stripe_customer_id:
            return stripe.Customer.retrieve(subscription.stripe_customer_id)
    except:
        pass
    
    # Create new customer
    customer = stripe.Customer.create(
        email=user.email,
        name=user.full_name,
        metadata={
            'user_id': str(user.id)
        }
    )
    
    return customer

def handle_payment_succeeded(invoice):
    """Handle successful payment webhook"""
    try:
        subscription = Subscription.objects.get(
            stripe_subscription_id=invoice['subscription']
        )
        
        # Update subscription status
        subscription.status = 'active'
        subscription.save()
        
        # Create payment record
        Payment.objects.create(
            user=subscription.user,
            subscription=subscription,
            amount=invoice['amount_paid'] / 100,  # Convert from cents
            currency=invoice['currency'].upper(),
            stripe_payment_intent_id=invoice['payment_intent'],
            status='succeeded',
            payment_method='card',
            description=f"Payment for {subscription.plan_type} subscription"
        )
        
    except Subscription.DoesNotExist:
        pass

def handle_payment_failed(invoice):
    """Handle failed payment webhook"""
    try:
        subscription = Subscription.objects.get(
            stripe_subscription_id=invoice['subscription']
        )
        
        # Update subscription status
        subscription.status = 'past_due'
        subscription.save()
        
        # Create failed payment record
        Payment.objects.create(
            user=subscription.user,
            subscription=subscription,
            amount=invoice['amount_due'] / 100,
            currency=invoice['currency'].upper(),
            stripe_payment_intent_id=invoice['payment_intent'],
            status='failed',
            payment_method='card',
            description=f"Failed payment for {subscription.plan_type} subscription"
        )
        
    except Subscription.DoesNotExist:
        pass

def handle_subscription_updated(stripe_subscription):
    """Handle subscription updated webhook"""
    try:
        subscription = Subscription.objects.get(
            stripe_subscription_id=stripe_subscription['id']
        )
        
        # Update subscription details
        subscription.status = stripe_subscription['status']
        subscription.current_period_start = timezone.datetime.fromtimestamp(
            stripe_subscription['current_period_start']
        )
        subscription.current_period_end = timezone.datetime.fromtimestamp(
            stripe_subscription['current_period_end']
        )
        subscription.cancel_at_period_end = stripe_subscription.get('cancel_at_period_end', False)
        
        subscription.save()
        
    except Subscription.DoesNotExist:
        pass

def handle_subscription_deleted(stripe_subscription):
    """Handle subscription deleted webhook"""
    try:
        subscription = Subscription.objects.get(
            stripe_subscription_id=stripe_subscription['id']
        )
        
        subscription.status = 'canceled'
        subscription.save()
        
    except Subscription.DoesNotExist:
        pass