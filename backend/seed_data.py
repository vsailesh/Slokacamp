import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'slokcamp.settings')
django.setup()

from django.contrib.auth import get_user_model
from courses.models import Course, Lesson, Review
from decimal import Decimal

User = get_user_model()

# Create admin user
admin, created = User.objects.get_or_create(
    email='admin@slokcamp.com',
    defaults={
        'full_name': 'Administrator',
        'role': 'admin',
        'is_staff': True,
        'is_superuser': True,
    }
)
if created:
    admin.set_password('Admin@123')
    admin.save()
    print(f'✓ Created admin user: {admin.email}')
else:
    print(f'✓ Admin user already exists: {admin.email}')

# Create test user
test_user, created = User.objects.get_or_create(
    email='test@example.com',
    defaults={
        'full_name': 'Test User',
        'role': 'user',
        'total_xp': 2450,
        'current_streak': 7,
    }
)
if created:
    test_user.set_password('Test@123')
    test_user.save()
    print(f'✓ Created test user: {test_user.email}')

# Sample courses data
courses_data = [
    {
        'title': 'Introduction to Sanskrit Slokas',
        'short_description': 'Learn the fundamentals of Sanskrit slokas with interactive lessons',
        'description': 'Master the basics of Sanskrit pronunciation, grammar, and sloka recitation. This beginner-friendly course will guide you through essential slokas from Bhagavad Gita.',
        'category': 'Sanskrit Slokas',
        'difficulty': 'beginner',
        'duration_hours': 12,
        'instructor_name': 'Dr. Priya Sharma',
        'instructor_bio': 'PhD in Sanskrit Studies with 15 years of teaching experience',
        'rating': Decimal('4.8'),
        'total_reviews': 245,
        'total_students': 1250,
        'thumbnail_image': 'https://images.unsplash.com/photo-1532012197267-da84d127e765?w=400',
    },
    {
        'title': 'Ayurvedic Fundamentals',
        'short_description': 'Discover the ancient science of Ayurveda and its healing principles',
        'description': 'A comprehensive introduction to Ayurvedic medicine, doshas, and natural healing methods. Learn to apply Ayurvedic principles in daily life.',
        'category': 'Ayurveda',
        'difficulty': 'beginner',
        'duration_hours': 16,
        'instructor_name': 'Vaidya Ramesh Kumar',
        'instructor_bio': 'Certified Ayurvedic practitioner with 20+ years experience',
        'rating': Decimal('4.9'),
        'total_reviews': 189,
        'total_students': 980,
        'thumbnail_image': 'https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=400',
    },
    {
        'title': 'Meditation Mastery',
        'short_description': 'Transform your mind through ancient meditation techniques',
        'description': 'Learn various meditation techniques from Vedic traditions. Includes guided meditations, breathing exercises, and mindfulness practices.',
        'category': 'Meditation',
        'difficulty': 'beginner',
        'duration_hours': 8,
        'instructor_name': 'Swami Ananda',
        'instructor_bio': 'Meditation teacher and spiritual guide for 25+ years',
        'rating': Decimal('4.7'),
        'total_reviews': 312,
        'total_students': 1450,
        'thumbnail_image': 'https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=400',
    },
    {
        'title': 'Yoga Philosophy Deep Dive',
        'short_description': 'Explore the philosophical foundations of yoga practice',
        'description': 'Study the Yoga Sutras of Patanjali and understand the eight limbs of yoga. Perfect for serious practitioners and teachers.',
        'category': 'Yoga Philosophy',
        'difficulty': 'intermediate',
        'duration_hours': 20,
        'instructor_name': 'Guru Sita Devi',
        'instructor_bio': 'E-RYT 500 certified yoga teacher and philosopher',
        'rating': Decimal('4.9'),
        'total_reviews': 156,
        'total_students': 720,
        'thumbnail_image': 'https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=400',
    },
]

# Create courses and lessons
for course_data in courses_data:
    course, created = Course.objects.get_or_create(
        title=course_data['title'],
        defaults=course_data
    )
    if created:
        print(f'✓ Created course: {course.title}')
        
        # Add lessons for each course
        for i in range(1, 13):
            Lesson.objects.create(
                course=course,
                title=f'Chapter {i}: Lesson Title',
                description=f'Learn important concepts in lesson {i}',
                lesson_type='video' if i % 3 != 0 else 'practice',
                order=i,
                duration_minutes=15 if i % 3 != 0 else 10,
                video_url='https://example.com/video',
                transcript='Sample transcript text...',
                xp_reward=10,
            )
        print(f'  ✓ Added 12 lessons to {course.title}')

print('\n✅ Database seeded successfully!')
print(f'\n📝 Admin Credentials:')
print(f'   Email: admin@slokcamp.com')
print(f'   Password: Admin@123')
