#!/bin/bash
# Comprehensive deployment script for Ayurveda E-Learning Platform
# Handles database setup, migrations, static files, and service startup

set -e  # Exit on any error

echo "Starting Ayurveda E-Learning Platform deployment..."

# Function to wait for service to be ready
wait_for_service() {
    local host=$1
    local port=$2
    local service_name=$3
    
    echo "Waiting for $service_name to be ready at $host:$port..."
    
    for i in {1..30}; do
        if nc -z "$host" "$port"; then
            echo "$service_name is ready!"
            return 0
        fi
        echo "Attempt $i: $service_name not ready yet, waiting 2 seconds..."
        sleep 2
    done
    
    echo "ERROR: $service_name failed to start within 60 seconds"
    exit 1
}

# Wait for PostgreSQL
wait_for_service "${DB_HOST:-postgres}" "${DB_PORT:-5432}" "PostgreSQL"

# Wait for Redis
wait_for_service "${REDIS_HOST:-redis}" "6379" "Redis"

echo "All dependencies are ready. Starting application setup..."

# Create necessary directories
mkdir -p /app/logs
mkdir -p /app/media
mkdir -p /app/staticfiles

# Set correct permissions
chown -R django:django /app/logs /app/media /app/staticfiles

echo "Running database migrations..."
python manage.py migrate --noinput

if [ "$?" -ne 0 ]; then
    echo "ERROR: Database migrations failed"
    exit 1
fi

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

if [ "$?" -ne 0 ]; then
    echo "ERROR: Static files collection failed"
    exit 1
fi

# Create superuser if it doesn't exist (only in development)
if [ "${DEBUG:-False}" = "True" ]; then
    echo "Creating development superuser..."
    python manage.py shell << EOF
from accounts.models import User
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@slokacamp.com',
        password='admin123',
        first_name='Admin',
        last_name='User'
    )
    print('Superuser created: admin / admin123')
else:
    print('Superuser already exists')
EOF
fi

# Load initial data if fixtures exist
if [ -d "fixtures" ] && [ "$(ls -A fixtures)" ]; then
    echo "Loading initial data..."
    for fixture in fixtures/*.json; do
        echo "Loading $fixture..."
        python manage.py loaddata "$fixture" || echo "Warning: Failed to load $fixture"
    done
fi

# Create default subscription plans
echo "Setting up default subscription plans..."
python manage.py shell << 'EOF'
from payments.models import SubscriptionPlan

plans = [
    {
        'name': 'Monthly Premium',
        'description': 'Full access to all courses and live classes',
        'price': 19.99,
        'billing_period': 'monthly',
        'stripe_price_id': 'price_monthly_premium',
        'stripe_product_id': 'prod_slokacamp_premium',
        'features': [
            'Unlimited access to all courses',
            'Live classes with expert instructors', 
            'Personalized learning paths',
            'Offline content downloads',
            'Priority support'
        ],
        'trial_period_days': 7
    },
    {
        'name': 'Yearly Premium',
        'description': 'Full access with 2 months free',
        'price': 199.99,
        'billing_period': 'yearly',
        'stripe_price_id': 'price_yearly_premium',
        'stripe_product_id': 'prod_slokacamp_premium',
        'features': [
            'Unlimited access to all courses',
            'Live classes with expert instructors',
            'Personalized learning paths', 
            'Offline content downloads',
            'Priority support',
            'Save 17% compared to monthly'
        ],
        'trial_period_days': 14
    }
]

for plan_data in plans:
    plan, created = SubscriptionPlan.objects.get_or_create(
        stripe_price_id=plan_data['stripe_price_id'],
        defaults=plan_data
    )
    if created:
        print(f"Created subscription plan: {plan.name}")
    else:
        print(f"Subscription plan already exists: {plan.name}")
EOF

# Validate critical environment variables
echo "Validating configuration..."

required_vars=("SECRET_KEY" "DB_NAME" "DB_USER" "DB_PASSWORD")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "ERROR: Required environment variable $var is not set"
        exit 1
    fi
done

echo "Setup completed successfully!"

# Start the application
exec "$@"