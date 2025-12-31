import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'slokcamp.settings')
django.setup()

from payments.models import SubscriptionPlan
from decimal import Decimal

# Create subscription plans
plans_data = [
    {
        'name': 'Basic Monthly',
        'plan_type': 'monthly',
        'price': Decimal('499.00'),
        'currency': 'INR',
        'course_access': 'basic',
        'max_devices': 1,
        'video_quality': 'hd',
        'download_enabled': False,
        'trial_days': 7,
        'is_active': True,
    },
    {
        'name': 'Premium Monthly',
        'plan_type': 'monthly',
        'price': Decimal('999.00'),
        'currency': 'INR',
        'course_access': 'all',
        'max_devices': 2,
        'video_quality': 'full_hd',
        'download_enabled': True,
        'trial_days': 14,
        'is_active': True,
    },
    {
        'name': 'Premium Yearly',
        'plan_type': 'yearly',
        'price': Decimal('9999.00'),
        'currency': 'INR',
        'course_access': 'all',
        'max_devices': 3,
        'video_quality': 'full_hd',
        'download_enabled': True,
        'trial_days': 30,
        'is_active': True,
    },
    {
        'name': 'Lifetime Access',
        'plan_type': 'lifetime',
        'price': Decimal('19999.00'),
        'currency': 'INR',
        'course_access': 'all',
        'max_devices': 5,
        'video_quality': 'full_hd',
        'download_enabled': True,
        'trial_days': 0,
        'is_active': True,
    },
]

print("Creating subscription plans...")
for plan_data in plans_data:
    plan, created = SubscriptionPlan.objects.get_or_create(
        name=plan_data['name'],
        defaults=plan_data
    )
    if created:
        print(f'✓ Created: {plan.name} - ₹{plan.price}/{plan.plan_type}')
    else:
        print(f'  Already exists: {plan.name}')

print(f'\n✅ Total plans: {SubscriptionPlan.objects.count()}')
