from django.db import models
from django.conf import settings
import uuid

class SubscriptionPlan(models.Model):
    PLAN_TYPES = (
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
        ('lifetime', 'Lifetime'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='INR')
    stripe_price_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    stripe_product_id = models.CharField(max_length=255, null=True, blank=True)
    
    # Features
    course_access = models.CharField(max_length=20, default='all', choices=[
        ('all', 'All Courses'),
        ('premium', 'Premium Only'),
        ('basic', 'Basic Only')
    ])
    max_devices = models.IntegerField(default=1)
    video_quality = models.CharField(max_length=10, default='hd', choices=[
        ('sd', 'Standard Definition'),
        ('hd', 'High Definition'),
        ('4k', '4K Ultra HD')
    ])
    download_enabled = models.BooleanField(default=False)
    
    trial_days = models.IntegerField(default=0, help_text='Free trial period in days')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'subscription_plans'
        ordering = ['price']

    def __str__(self):
        return f"{self.name} - ₹{self.price}/{self.plan_type}"


class Subscription(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('trialing', 'Trial'),
        ('past_due', 'Past Due'),
        ('canceled', 'Canceled'),
        ('expired', 'Expired'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='subscription', on_delete=models.CASCADE)
    plan = models.ForeignKey(SubscriptionPlan, related_name='subscriptions', on_delete=models.PROTECT)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='trialing')
    stripe_subscription_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    stripe_customer_id = models.CharField(max_length=255, null=True, blank=True)
    
    current_period_start = models.DateTimeField()
    current_period_end = models.DateTimeField()
    trial_end = models.DateTimeField(null=True, blank=True)
    
    auto_renew = models.BooleanField(default=True)
    canceled_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'subscriptions'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.plan.name} ({self.status})"
    
    def is_valid(self):
        """Check if subscription is currently valid"""
        from django.utils import timezone
        return self.status in ['active', 'trialing'] and self.current_period_end > timezone.now()


class Payment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('succeeded', 'Succeeded'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='payments', on_delete=models.CASCADE)
    subscription = models.ForeignKey(Subscription, related_name='payments', on_delete=models.SET_NULL, null=True, blank=True)
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='INR')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    stripe_payment_intent_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    stripe_invoice_id = models.CharField(max_length=255, null=True, blank=True)
    
    payment_method = models.CharField(max_length=50, default='card')
    failure_reason = models.TextField(blank=True)
    
    metadata = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payments'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - ₹{self.amount} ({self.status})"


class StripeWebhookEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    stripe_event_id = models.CharField(max_length=255, unique=True)
    event_type = models.CharField(max_length=100)
    payload = models.JSONField()
    processed = models.BooleanField(default=False)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'stripe_webhook_events'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['stripe_event_id']),
            models.Index(fields=['event_type', '-created_at']),
        ]

    def __str__(self):
        return f"{self.event_type} - {self.stripe_event_id}"
