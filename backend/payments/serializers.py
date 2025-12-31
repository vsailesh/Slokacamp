from rest_framework import serializers
from .models import SubscriptionPlan, Subscription, Payment

class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = (
            'id', 'name', 'plan_type', 'price', 'currency',
            'course_access', 'max_devices', 'video_quality',
            'download_enabled', 'trial_days', 'is_active'
        )

class SubscriptionSerializer(serializers.ModelSerializer):
    plan = SubscriptionPlanSerializer(read_only=True)
    is_valid = serializers.SerializerMethodField()
    days_remaining = serializers.SerializerMethodField()
    
    class Meta:
        model = Subscription
        fields = (
            'id', 'plan', 'status', 'current_period_start',
            'current_period_end', 'trial_end', 'auto_renew',
            'canceled_at', 'is_valid', 'days_remaining', 'created_at'
        )
    
    def get_is_valid(self, obj):
        return obj.is_valid()
    
    def get_days_remaining(self, obj):
        from django.utils import timezone
        if obj.current_period_end > timezone.now():
            delta = obj.current_period_end - timezone.now()
            return delta.days
        return 0

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = (
            'id', 'amount', 'currency', 'status',
            'payment_method', 'created_at'
        )

class CreateCheckoutSessionSerializer(serializers.Serializer):
    plan_id = serializers.UUIDField()
    success_url = serializers.URLField()
    cancel_url = serializers.URLField()
