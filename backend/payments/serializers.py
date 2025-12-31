from rest_framework import serializers
from .models import SubscriptionPlan, Subscription, Payment
from accounts.serializers import UserSerializer

class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = '__all__'
        read_only_fields = ('stripe_price_id', 'stripe_product_id', 'created_at', 'updated_at')

class SubscriptionSerializer(serializers.ModelSerializer):
    plan = SubscriptionPlanSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    is_valid = serializers.SerializerMethodField()
    
    class Meta:
        model = Subscription
        fields = '__all__'
        read_only_fields = (
            'stripe_subscription_id', 'stripe_customer_id',
            'status', 'current_period_start', 'current_period_end',
            'trial_end', 'canceled_at', 'created_at', 'updated_at'
        )
    
    def get_is_valid(self, obj):
        return obj.is_valid()

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class CreateCheckoutSessionSerializer(serializers.Serializer):
    plan_id = serializers.UUIDField(required=True)
    success_url = serializers.URLField(required=True)
    cancel_url = serializers.URLField(required=True)
