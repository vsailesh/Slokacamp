from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Avg, Sum
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Course, Chapter, Lesson, Enrollment, LessonProgress
from .serializers import (
    CourseSerializer,
    CourseDetailSerializer,
    EnrollmentSerializer,
    LessonProgressSerializer,
    DashboardSerializer,
    LessonSerializer
)
from accounts.models import UserProfile

class CourseListView(generics.ListAPIView):
    """List courses with filtering and search"""
    serializer_class = CourseSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = Course.objects.filter(is_published=True)
        
        # Filtering
        category = self.request.query_params.get('category')
        level = self.request.query_params.get('level')
        is_free = self.request.query_params.get('is_free')
        search = self.request.query_params.get('search')
        
        if category:
            queryset = queryset.filter(category=category)
        
        if level:
            queryset = queryset.filter(level=level)
        
        if is_free is not None:
            is_free_bool = is_free.lower() == 'true'
            queryset = queryset.filter(is_free=is_free_bool)
        
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(instructor_name__icontains=search)
            )
        
        # Ordering
        ordering = self.request.query_params.get('ordering', '-created_at')
        if ordering == 'popular':
            queryset = queryset.order_by('-enrollment_count', '-view_count')
        elif ordering == 'rating':
            queryset = queryset.order_by('-average_rating')
        else:
            queryset = queryset.order_by(ordering)
        
        return queryset

class CourseDetailView(generics.RetrieveAPIView):
    """Get detailed course information"""
    serializer_class = CourseDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = 'id'
    
    def get_queryset(self):
        return Course.objects.filter(is_published=True).prefetch_related(
            'chapters__lessons',
            'prerequisites'
        )
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Increment view count
        instance.view_count += 1
        instance.save(update_fields=['view_count'])
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

@swagger_auto_schema(
    method='post',
    request_body=EnrollmentSerializer,
    responses={
        201: EnrollmentSerializer,
        400: 'Bad Request - Validation errors',
        403: 'Forbidden - Subscription required'
    },
    operation_description='Enroll in a course'
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def enroll_course(request, course_id):
    """Enroll user in a course"""
    try:
        course = Course.objects.get(id=course_id, is_published=True)
    except Course.DoesNotExist:
        return Response({
            'error': 'Course not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Check if already enrolled
    if Enrollment.objects.filter(user=request.user, course=course).exists():
        return Response({
            'error': 'Already enrolled in this course'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check subscription requirement
    if course.requires_subscription and not request.user.is_subscription_active:
        return Response({
            'error': 'Subscription required',
            'message': 'This course requires an active subscription to access.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Create enrollment
    enrollment_data = {
        'course_id': course_id,
        'payment_method': 'subscription' if course.requires_subscription else 'free'
    }
    
    serializer = EnrollmentSerializer(
        data=enrollment_data,
        context={'request': request}
    )
    
    if serializer.is_valid():
        enrollment = serializer.save()
        
        # Update course enrollment count
        course.enrollment_count += 1
        course.save(update_fields=['enrollment_count'])
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='get',
    responses={200: EnrollmentSerializer(many=True)},
    operation_description='List user enrollments'
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_enrollments(request):
    """List all enrollments for the current user"""
    enrollments = Enrollment.objects.filter(
        user=request.user
    ).select_related('course').order_by('-enrolled_at')
    
    # Filter by status if provided
    status_filter = request.query_params.get('status')
    if status_filter:
        enrollments = enrollments.filter(status=status_filter)
    
    serializer = EnrollmentSerializer(enrollments, many=True)
    return Response(serializer.data)

@swagger_auto_schema(
    method='get',
    responses={200: LessonSerializer},
    operation_description='Get lesson details'
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def lesson_detail(request, lesson_id):
    """Get detailed lesson information"""
    lesson = get_object_or_404(Lesson, id=lesson_id, is_published=True)
    
    # Check enrollment
    enrollment = Enrollment.objects.filter(
        user=request.user,
        course=lesson.course,
        status='active'
    ).first()
    
    if not enrollment and not lesson.is_preview:
        return Response({
            'error': 'Enrollment required',
            'message': 'You must be enrolled in this course to access this lesson.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Create or update lesson progress
    if enrollment:
        progress, created = LessonProgress.objects.get_or_create(
            user=request.user,
            lesson=lesson,
            enrollment=enrollment
        )
        
        if progress.status == 'not_started':
            progress.status = 'in_progress'
            progress.save(update_fields=['status'])
    
    serializer = LessonSerializer(lesson, context={'request': request})
    return Response(serializer.data)

@swagger_auto_schema(
    method='patch',
    request_body=LessonProgressSerializer,
    responses={200: LessonProgressSerializer},
    operation_description='Update lesson progress'
)
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_lesson_progress(request, lesson_id):
    """Update progress for a specific lesson"""
    lesson = get_object_or_404(Lesson, id=lesson_id)
    
    # Get or create lesson progress
    enrollment = get_object_or_404(
        Enrollment,
        user=request.user,
        course=lesson.course,
        status='active'
    )
    
    progress, created = LessonProgress.objects.get_or_create(
        user=request.user,
        lesson=lesson,
        enrollment=enrollment
    )
    
    serializer = LessonProgressSerializer(
        progress,
        data=request.data,
        partial=True
    )
    
    if serializer.is_valid():
        serializer.save()
        
        # Update enrollment progress if lesson completed
        if progress.status == 'completed':
            update_enrollment_progress(enrollment)
        
        return Response(serializer.data)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='get',
    responses={200: DashboardSerializer},
    operation_description='Get user dashboard data'
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_dashboard(request):
    """Get personalized dashboard data for the user"""
    user = request.user
    profile = getattr(user, 'profile', None) or UserProfile.objects.create(user=user)
    
    # User statistics
    enrollments = Enrollment.objects.filter(user=user)
    completed_courses = enrollments.filter(status='completed').count()
    active_enrollments = enrollments.filter(status='active')
    
    user_stats = {
        'total_watch_time': profile.total_watch_time,
        'courses_completed': completed_courses,
        'courses_in_progress': active_enrollments.count(),
        'current_streak': profile.streak_days,
        'total_xp': 0,  # Calculate based on progress
    }
    
    # Continue learning (active enrollments with recent progress)
    continue_learning = active_enrollments.filter(
        progress_percentage__gt=0,
        progress_percentage__lt=100
    ).order_by('-last_accessed_at')[:5]
    
    # Recommended courses based on user preferences and history
    recommended_courses = get_recommended_courses(user)[:6]
    
    # Recent activity
    recent_activity = get_recent_activity(user)[:10]
    
    # Upcoming live classes (mock data for now)
    upcoming_live_classes = []
    
    dashboard_data = {
        'user_stats': user_stats,
        'continue_learning': continue_learning,
        'recommended_courses': recommended_courses,
        'recent_activity': recent_activity,
        'upcoming_live_classes': upcoming_live_classes
    }
    
    serializer = DashboardSerializer(dashboard_data)
    return Response(serializer.data)

# Utility functions

def update_enrollment_progress(enrollment):
    """Update enrollment progress based on completed lessons"""
    total_lessons = Lesson.objects.filter(
        chapter__course=enrollment.course,
        is_published=True
    ).count()
    
    completed_lessons = LessonProgress.objects.filter(
        enrollment=enrollment,
        status='completed'
    ).count()
    
    if total_lessons > 0:
        progress_percentage = (completed_lessons / total_lessons) * 100
        enrollment.progress_percentage = progress_percentage
        enrollment.lessons_completed = completed_lessons
        enrollment.last_accessed_at = timezone.now()
        
        # Mark as completed if all lessons are done
        if progress_percentage >= 100 and enrollment.status != 'completed':
            enrollment.status = 'completed'
            enrollment.completed_at = timezone.now()
        
        enrollment.save()

def get_recommended_courses(user):
    """Get personalized course recommendations for user"""
    # Get user's enrolled course categories
    user_categories = Enrollment.objects.filter(
        user=user
    ).values_list('course__category', flat=True).distinct()
    
    # Get popular courses in similar categories
    recommended = Course.objects.filter(
        is_published=True,
        category__in=user_categories
    ).exclude(
        id__in=Enrollment.objects.filter(user=user).values_list('course_id', flat=True)
    ).order_by('-average_rating', '-enrollment_count')[:6]
    
    # If not enough recommendations, add popular courses from other categories
    if len(recommended) < 6:
        additional = Course.objects.filter(
            is_published=True
        ).exclude(
            id__in=Enrollment.objects.filter(user=user).values_list('course_id', flat=True)
        ).exclude(
            id__in=[c.id for c in recommended]
        ).order_by('-enrollment_count')[:6-len(recommended)]
        
        recommended = list(recommended) + list(additional)
    
    return recommended

def get_recent_activity(user):
    """Get recent learning activity for user"""
    activities = []
    
    # Recent lesson progress
    recent_progress = LessonProgress.objects.filter(
        user=user,
        last_accessed_at__isnull=False
    ).select_related('lesson', 'lesson__chapter__course').order_by('-last_accessed_at')[:5]
    
    for progress in recent_progress:
        activities.append({
            'type': 'lesson_progress',
            'title': progress.lesson.title,
            'course_title': progress.lesson.course.title,
            'status': progress.status,
            'timestamp': progress.last_accessed_at,
            'completion_percentage': float(progress.completion_percentage)
        })
    
    # Recent enrollments
    recent_enrollments = Enrollment.objects.filter(
        user=user
    ).select_related('course').order_by('-enrolled_at')[:3]
    
    for enrollment in recent_enrollments:
        activities.append({
            'type': 'course_enrollment',
            'title': f"Enrolled in {enrollment.course.title}",
            'course_title': enrollment.course.title,
            'timestamp': enrollment.enrolled_at
        })
    
    # Sort all activities by timestamp
    activities.sort(key=lambda x: x['timestamp'], reverse=True)
    
    return activities[:10]