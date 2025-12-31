from django.contrib import admin
from .models import SubscriptionPlan, Subscription, Payment, StripeWebhookEvent

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'plan_type', 'price', 'currency', 'max_devices', 'trial_days', 'is_active')
    list_filter = ('plan_type', 'is_active', 'course_access')
    search_fields = ('name', 'stripe_price_id', 'stripe_product_id')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Plan Details', {
            'fields': ('name', 'plan_type', 'price', 'currency')
        }),
        ('Stripe Integration', {
            'fields': ('stripe_price_id', 'stripe_product_id')
        }),
        ('Features', {
            'fields': ('course_access', 'max_devices', 'video_quality', 'download_enabled')
        }),
        ('Trial & Status', {
            'fields': ('trial_days', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'status', 'current_period_end', 'auto_renew', 'created_at')
    list_filter = ('status', 'auto_renew', 'created_at')
    search_fields = ('user__email', 'stripe_subscription_id', 'stripe_customer_id')
    readonly_fields = ('created_at', 'updated_at', 'is_valid_display')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Subscription Info', {
            'fields': ('user', 'plan', 'status')
        }),
        ('Stripe Integration', {
            'fields': ('stripe_subscription_id', 'stripe_customer_id')
        }),
        ('Billing Period', {
            'fields': ('current_period_start', 'current_period_end', 'trial_end')
        }),
        ('Status', {
            'fields': ('auto_renew', 'canceled_at', 'is_valid_display')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def is_valid_display(self, obj):
        return "✓ Active" if obj.is_valid() else "✗ Expired"
    is_valid_display.short_description = 'Validity'

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'currency', 'status', 'payment_method', 'created_at')
    list_filter = ('status', 'currency', 'payment_method', 'created_at')
    search_fields = ('user__email', 'stripe_payment_intent_id', 'stripe_invoice_id')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Payment Info', {
            'fields': ('user', 'subscription', 'amount', 'currency', 'status')
        }),
        ('Stripe Integration', {
            'fields': ('stripe_payment_intent_id', 'stripe_invoice_id')
        }),
        ('Details', {
            'fields': ('payment_method', 'failure_reason', 'metadata')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(StripeWebhookEvent)
class StripeWebhookEventAdmin(admin.ModelAdmin):
    list_display = ('stripe_event_id', 'event_type', 'processed', 'created_at')
    list_filter = ('event_type', 'processed', 'created_at')
    search_fields = ('stripe_event_id', 'event_type')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Event Info', {
            'fields': ('stripe_event_id', 'event_type', 'processed')
        }),
        ('Payload', {
            'fields': ('payload', 'error_message'),
            'classes': ('collapse',)
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        }),
    )
