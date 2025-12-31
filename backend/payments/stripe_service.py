import stripe
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import Subscription, Payment, SubscriptionPlan, StripeWebhookEvent
from device_management.models import AuditLog

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

class StripeService:
    
    @staticmethod
    def create_customer(user):
        """Create Stripe customer for user"""
        try:
            customer = stripe.Customer.create(
                email=user.email,
                name=user.full_name,
                metadata={'user_id': str(user.id)}
            )
            return customer.id
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe customer creation failed: {str(e)}")
    
    @staticmethod
    def create_checkout_session(user, plan, success_url, cancel_url):
        """Create Stripe Checkout session for subscription"""
        try:
            # Get or create Stripe customer
            if hasattr(user, 'subscription') and user.subscription.stripe_customer_id:
                customer_id = user.subscription.stripe_customer_id
            else:
                customer_id = StripeService.create_customer(user)
            
            # Determine subscription mode
            if plan.plan_type == 'lifetime':
                mode = 'payment'
                line_items = [{
                    'price_data': {
                        'currency': plan.currency.lower(),
                        'product_data': {
                            'name': plan.name,
                            'description': f'Lifetime access to {plan.course_access} courses',
                        },
                        'unit_amount': int(plan.price * 100),  # Convert to cents
                    },
                    'quantity': 1,
                }]
            else:
                mode = 'subscription'
                line_items = [{
                    'price': plan.stripe_price_id,
                    'quantity': 1,
                }]
            
            # Create checkout session
            checkout_session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=['card'],
                line_items=line_items,
                mode=mode,
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    'user_id': str(user.id),
                    'plan_id': str(plan.id),
                },
                subscription_data={
                    'trial_period_days': plan.trial_days,
                    'metadata': {
                        'user_id': str(user.id),
                        'plan_id': str(plan.id),
                    }
                } if mode == 'subscription' and plan.trial_days > 0 else None,
            )
            
            return checkout_session
            
        except stripe.error.StripeError as e:
            raise Exception(f"Checkout session creation failed: {str(e)}")
    
    @staticmethod
    def create_subscription(user, plan, stripe_subscription_id, stripe_customer_id):
        """Create or update subscription in database"""
        try:
            # Retrieve Stripe subscription
            stripe_sub = stripe.Subscription.retrieve(stripe_subscription_id)
            
            # Calculate dates
            current_period_start = timezone.datetime.fromtimestamp(
                stripe_sub.current_period_start, tz=timezone.utc
            )
            current_period_end = timezone.datetime.fromtimestamp(
                stripe_sub.current_period_end, tz=timezone.utc
            )
            trial_end = None
            if stripe_sub.trial_end:
                trial_end = timezone.datetime.fromtimestamp(
                    stripe_sub.trial_end, tz=timezone.utc
                )
            
            # Create or update subscription
            subscription, created = Subscription.objects.update_or_create(
                user=user,
                defaults={
                    'plan': plan,
                    'status': stripe_sub.status,
                    'stripe_subscription_id': stripe_subscription_id,
                    'stripe_customer_id': stripe_customer_id,
                    'current_period_start': current_period_start,
                    'current_period_end': current_period_end,
                    'trial_end': trial_end,
                    'auto_renew': stripe_sub.cancel_at_period_end == False,
                }
            )
            
            return subscription
            
        except Exception as e:
            raise Exception(f"Subscription creation failed: {str(e)}")
    
    @staticmethod
    def cancel_subscription(subscription):
        \"\"\"Cancel subscription at period end\"\"\"
        try:
            stripe.Subscription.modify(
                subscription.stripe_subscription_id,
                cancel_at_period_end=True
            )
            
            subscription.auto_renew = False
            subscription.canceled_at = timezone.now()
            subscription.save()
            
            return True
            
        except stripe.error.StripeError as e:
            raise Exception(f"Subscription cancellation failed: {str(e)}")
    
    @staticmethod
    def reactivate_subscription(subscription):
        \"\"\"Reactivate a canceled subscription\"\"\"
        try:
            stripe.Subscription.modify(
                subscription.stripe_subscription_id,
                cancel_at_period_end=False
            )
            
            subscription.auto_renew = True
            subscription.canceled_at = None
            subscription.save()
            
            return True
            
        except stripe.error.StripeError as e:
            raise Exception(f"Subscription reactivation failed: {str(e)}")
    
    @staticmethod
    def handle_webhook_event(payload, sig_header):
        \"\"\"Process Stripe webhook events\"\"\"
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError:
            raise Exception("Invalid payload")
        except stripe.error.SignatureVerificationError:
            raise Exception("Invalid signature")
        
        # Store webhook event
        webhook_event = StripeWebhookEvent.objects.create(
            stripe_event_id=event.id,
            event_type=event.type,
            payload=event.data
        )
        
        try:
            # Handle different event types
            if event.type == 'checkout.session.completed':
                StripeService._handle_checkout_completed(event.data.object)
            
            elif event.type == 'customer.subscription.updated':
                StripeService._handle_subscription_updated(event.data.object)
            
            elif event.type == 'customer.subscription.deleted':
                StripeService._handle_subscription_deleted(event.data.object)
            
            elif event.type == 'invoice.payment_succeeded':
                StripeService._handle_payment_succeeded(event.data.object)
            
            elif event.type == 'invoice.payment_failed':
                StripeService._handle_payment_failed(event.data.object)
            
            webhook_event.processed = True
            webhook_event.save()
            
        except Exception as e:
            webhook_event.error_message = str(e)
            webhook_event.save()
            raise
        
        return event
    
    @staticmethod
    def _handle_checkout_completed(session):
        \"\"\"Handle successful checkout\"\"\"
        from accounts.models import User
        
        user_id = session.metadata.get('user_id')
        plan_id = session.metadata.get('plan_id')
        
        if not user_id or not plan_id:
            return
        
        user = User.objects.get(id=user_id)
        plan = SubscriptionPlan.objects.get(id=plan_id)
        
        if session.mode == 'subscription':
            # Create subscription
            StripeService.create_subscription(
                user, plan,
                session.subscription,
                session.customer
            )
            
            # Log audit
            AuditLog.objects.create(
                user=user,
                action='subscription_start',
                metadata={
                    'plan': plan.name,
                    'stripe_subscription_id': session.subscription
                }
            )
    
    @staticmethod
    def _handle_subscription_updated(subscription):
        \"\"\"Handle subscription status changes\"\"\"
        try:
            sub = Subscription.objects.get(stripe_subscription_id=subscription.id)
            sub.status = subscription.status
            sub.current_period_end = timezone.datetime.fromtimestamp(
                subscription.current_period_end, tz=timezone.utc
            )
            sub.save()
        except Subscription.DoesNotExist:
            pass
    
    @staticmethod
    def _handle_subscription_deleted(subscription):
        \"\"\"Handle subscription deletion\"\"\"
        try:
            sub = Subscription.objects.get(stripe_subscription_id=subscription.id)
            sub.status = 'expired'
            sub.save()
            
            # Log audit
            AuditLog.objects.create(
                user=sub.user,
                action='subscription_end',
                metadata={
                    'plan': sub.plan.name,
                    'reason': 'deleted'
                }
            )
        except Subscription.DoesNotExist:
            pass
    
    @staticmethod
    def _handle_payment_succeeded(invoice):
        \"\"\"Handle successful payment\"\"\"
        from accounts.models import User
        
        if not invoice.subscription:
            return
        
        try:
            sub = Subscription.objects.get(stripe_subscription_id=invoice.subscription)
            
            # Create payment record
            Payment.objects.create(
                user=sub.user,
                subscription=sub,
                amount=invoice.amount_paid / 100,  # Convert from cents
                currency=invoice.currency.upper(),
                status='succeeded',
                stripe_payment_intent_id=invoice.payment_intent,
                stripe_invoice_id=invoice.id,
                payment_method='card',
                metadata={'invoice': invoice.id}
            )
            
            # Log audit
            AuditLog.objects.create(
                user=sub.user,
                action='payment',
                metadata={
                    'amount': invoice.amount_paid / 100,
                    'currency': invoice.currency.upper(),
                    'invoice_id': invoice.id
                }
            )
        except Subscription.DoesNotExist:
            pass
    
    @staticmethod
    def _handle_payment_failed(invoice):
        \"\"\"Handle failed payment\"\"\"
        try:
            sub = Subscription.objects.get(stripe_subscription_id=invoice.subscription)
            sub.status = 'past_due'
            sub.save()
            
            # Create failed payment record
            Payment.objects.create(
                user=sub.user,
                subscription=sub,
                amount=invoice.amount_due / 100,
                currency=invoice.currency.upper(),
                status='failed',
                stripe_invoice_id=invoice.id,
                payment_method='card',
                failure_reason='Payment failed',
                metadata={'invoice': invoice.id}
            )
        except Subscription.DoesNotExist:
            pass
