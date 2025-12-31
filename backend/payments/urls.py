from django.urls import path
from .views import (
    SubscriptionPlanListView, MySubscriptionView,
    CreateCheckoutSessionView, CancelSubscriptionView,
    ReactivateSubscriptionView, PaymentHistoryView,
    StripeWebhookView
)

app_name = 'payments'

urlpatterns = [
    # Subscription Plans
    path('plans/', SubscriptionPlanListView.as_view(), name='subscription_plans'),
    
    # User Subscription Management
    path('my-subscription/', MySubscriptionView.as_view(), name='my_subscription'),
    path('checkout/', CreateCheckoutSessionView.as_view(), name='create_checkout'),
    path('cancel/', CancelSubscriptionView.as_view(), name='cancel_subscription'),
    path('reactivate/', ReactivateSubscriptionView.as_view(), name='reactivate_subscription'),
    
    # Payment History
    path('history/', PaymentHistoryView.as_view(), name='payment_history'),
    
    # Stripe Webhooks
    path('webhook/', StripeWebhookView.as_view(), name='stripe_webhook'),
]
