from django.db import models
from django.conf import settings
import uuid
from django.utils import timezone

class Subscription(models.Model):
    """User subscription model for premium access"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscription')
    
    # Subscription details
    plan_type = models.CharField(max_length=20, choices=[
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
        ('lifetime', 'Lifetime'),
        ('trial', 'Free Trial'),
    ])
    
    # Stripe integration
    stripe_subscription_id = serializers.CharField(max_length=255, unique=True, null=True, blank=True)
    stripe_customer_id = models.CharField(max_length=255, null=True, blank=True)
    stripe_payment_method_id = models.CharField(max_length=255, null=True, blank=True)
    
    # Subscription status
    status = models.CharField(max_length=20, choices=[
        ('active', 'Active'),
        ('past_due', 'Past Due'),
        ('canceled', 'Canceled'),
        ('incomplete', 'Incomplete'),
        ('incomplete_expired', 'Incomplete Expired'),
        ('trialing', 'Trialing'),
        ('unpaid', 'Unpaid'),
    ], default='incomplete')
    
    # Pricing and billing
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    
    # Subscription period
    current_period_start = models.DateTimeField()
    current_period_end = models.DateTimeField()
    cancel_at_period_end = models.BooleanField(default=False)
    canceled_at = models.DateTimeField(null=True, blank=True)
    
    # Trial information
    trial_start = models.DateTimeField(null=True, blank=True)
    trial_end = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'subscriptions'
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['stripe_subscription_id']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.plan_type} ({self.status})"
    
    @property
    def is_active(self):
        """Check if subscription is currently active"""
        if self.status not in ['active', 'trialing']:
            return False
        
        return self.current_period_end > timezone.now()
    
    @property
    def days_until_renewal(self):
        """Days until next renewal or expiration"""
        if self.current_period_end:
            delta = self.current_period_end - timezone.now()
            return max(0, delta.days)
        return 0

class SubscriptionPlan(models.Model):
    """Available subscription plans"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Plan details
    name = models.CharField(max_length=100)
    description = models.TextField()
    
    # Pricing
    price = models.DecimalField(max_digits=8, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    billing_period = models.CharField(max_length=10, choices=[
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
        ('lifetime', 'Lifetime'),
    ])
    
    # Stripe configuration
    stripe_price_id = models.CharField(max_length=255, unique=True)
    stripe_product_id = models.CharField(max_length=255)
    
    # Plan features
    features = models.JSONField(default=list)
    max_devices = models.PositiveIntegerField(default=1)
    max_downloads = models.PositiveIntegerField(default=0)  # 0 = unlimited
    
    # Plan availability
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    # Trial configuration
    trial_period_days = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'subscription_plans'
        verbose_name = 'Subscription Plan'
        verbose_name_plural = 'Subscription Plans'
        ordering = ['price']
    
    def __str__(self):
        return f"{self.name} - {self.price} {self.currency}/{self.billing_period}"

class Payment(models.Model):
    """Payment transaction records"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
    
    # Payment details
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    
    # Stripe integration
    stripe_payment_intent_id = models.CharField(max_length=255, unique=True)
    stripe_charge_id = models.CharField(max_length=255, null=True, blank=True)
    
    # Payment status
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('succeeded', 'Succeeded'),
        ('failed', 'Failed'),
        ('canceled', 'Canceled'),
        ('refunded', 'Refunded'),
    ])
    
    # Payment method
    payment_method = models.CharField(max_length=50, choices=[
        ('card', 'Credit/Debit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('paypal', 'PayPal'),
        ('apple_pay', 'Apple Pay'),
        ('google_pay', 'Google Pay'),
    ])
    
    # Transaction metadata
    description = models.CharField(max_length=255)
    metadata = models.JSONField(default=dict, blank=True)
    
    # Failure information
    failure_code = models.CharField(max_length=50, null=True, blank=True)
    failure_message = models.TextField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payments'
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['stripe_payment_intent_id']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.amount} {self.currency} ({self.status})"

class RefundRequest(models.Model):
    """User refund requests"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='refund_requests')
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='refund_requests')
    
    # Refund details
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    reason = models.CharField(max_length=100, choices=[
        ('not_satisfied', 'Not Satisfied'),
        ('technical_issues', 'Technical Issues'),
        ('billing_error', 'Billing Error'),
        ('accidental_purchase', 'Accidental Purchase'),
        ('other', 'Other'),
    ])
    
    description = models.TextField(blank=True)
    
    # Refund status
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('processed', 'Processed'),
    ], default='pending')
    
    # Admin review
    admin_notes = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='reviewed_refunds'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    # Stripe refund ID
    stripe_refund_id = models.CharField(max_length=255, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'refund_requests'
        verbose_name = 'Refund Request'
        verbose_name_plural = 'Refund Requests'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Refund Request - {self.user.email} - {self.amount} ({self.status})"