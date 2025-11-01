from rest_framework import serializers
from .models import Subscription, SubscriptionPlan, Payment, RefundRequest
from django.utils import timezone

class SubscriptionPlanSerializer(serializers.ModelSerializer):
    """Subscription plan serializer for public API"""
    
    class Meta:
        model = SubscriptionPlan
        fields = [
            'id', 'name', 'description', 'price', 'currency',
            'billing_period', 'features', 'is_featured',
            'trial_period_days'
        ]

class SubscriptionSerializer(serializers.ModelSerializer):
    """Subscription serializer"""
    plan_name = serializers.CharField(source='plan_type', read_only=True)
    is_active = serializers.ReadOnlyField()
    days_until_renewal = serializers.ReadOnlyField()
    
    class Meta:
        model = Subscription
        fields = [
            'id', 'plan_name', 'plan_type', 'status', 'amount', 'currency',
            'current_period_start', 'current_period_end', 'cancel_at_period_end',
            'is_active', 'days_until_renewal', 'trial_start', 'trial_end',
            'created_at'
        ]
        read_only_fields = [
            'id', 'status', 'current_period_start', 'current_period_end',
            'created_at'
        ]

class SubscriptionCreateSerializer(serializers.Serializer):
    """Subscription creation serializer"""
    plan_id = serializers.UUIDField()
    payment_method_id = serializers.CharField(max_length=255)
    
    def validate_plan_id(self, value):
        try:
            SubscriptionPlan.objects.get(id=value, is_active=True)
        except SubscriptionPlan.DoesNotExist:
            raise serializers.ValidationError("Invalid subscription plan")
        return value

class PaymentSerializer(serializers.ModelSerializer):
    """Payment history serializer"""
    
    class Meta:
        model = Payment
        fields = [
            'id', 'amount', 'currency', 'status', 'payment_method',
            'description', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class RefundRequestSerializer(serializers.ModelSerializer):
    """Refund request serializer"""
    payment_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = RefundRequest
        fields = [
            'id', 'payment_id', 'amount', 'reason', 'description',
            'status', 'created_at'
        ]
        read_only_fields = ['id', 'status', 'created_at']
    
    def validate_payment_id(self, value):
        request = self.context.get('request')
        try:
            payment = Payment.objects.get(
                id=value,
                user=request.user,
                status='succeeded'
            )
            
            # Check if refund already exists
            if RefundRequest.objects.filter(payment=payment).exists():
                raise serializers.ValidationError(
                    "Refund request already exists for this payment"
                )
            
            # Check if payment is within refund window (30 days)
            if (timezone.now() - payment.created_at).days > 30:
                raise serializers.ValidationError(
                    "Refund requests must be made within 30 days of payment"
                )
            
            return payment
        except Payment.DoesNotExist:
            raise serializers.ValidationError("Payment not found or invalid")
    
    def create(self, validated_data):
        payment = validated_data.pop('payment_id')
        return RefundRequest.objects.create(
            user=self.context['request'].user,
            payment=payment,
            **validated_data
        )