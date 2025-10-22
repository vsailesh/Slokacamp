from rest_framework import serializers
from .models import Course, Chapter, Lesson, Enrollment, LessonProgress
from django.db.models import Avg, Count

class LessonSerializer(serializers.ModelSerializer):
    """Lesson serializer with progress information"""
    progress = serializers.SerializerMethodField()
    
    class Meta:
        model = Lesson
        fields = [
            'id', 'title', 'description', 'order', 'content_type', 
            'duration', 'difficulty', 'is_preview', 'video_id',
            'sanskrit_text', 'transliteration', 'translation',
            'view_count', 'progress'
        ]
    
    def get_progress(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                progress = LessonProgress.objects.get(
                    user=request.user,
                    lesson=obj
                )
                return {
                    'status': progress.status,
                    'completion_percentage': float(progress.completion_percentage),
                    'last_position': progress.last_position,
                    'watch_time': progress.watch_time
                }
            except LessonProgress.DoesNotExist:
                return {
                    'status': 'not_started',
                    'completion_percentage': 0.0,
                    'last_position': 0,
                    'watch_time': 0
                }
        return None

class ChapterSerializer(serializers.ModelSerializer):
    """Chapter serializer with lessons"""
    lessons = LessonSerializer(many=True, read_only=True)
    lessons_count = serializers.IntegerField(source='lessons.count', read_only=True)
    
    class Meta:
        model = Chapter
        fields = [
            'id', 'title', 'description', 'order', 'is_published',
            'lessons', 'lessons_count'
        ]

class CourseSerializer(serializers.ModelSerializer):
    """Course serializer for API responses"""
    instructor_info = serializers.SerializerMethodField()
    enrollment_status = serializers.SerializerMethodField()
    chapters_count = serializers.IntegerField(source='chapters.count', read_only=True)
    total_lessons = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'description', 'short_description',
            'category', 'subcategory', 'level', 'thumbnail', 'trailer_video',
            'estimated_duration', 'instructor_info', 'is_free', 'requires_subscription',
            'price', 'is_published', 'is_featured', 'view_count', 'enrollment_count',
            'average_rating', 'total_ratings', 'learning_objectives', 'skills_gained',
            'enrollment_status', 'chapters_count', 'total_lessons', 'created_at'
        ]
    
    def get_instructor_info(self, obj):
        return {
            'name': obj.instructor_name,
            'bio': obj.instructor_bio,
            'image': obj.instructor_image,
            'credentials': obj.instructor_credentials
        }
    
    def get_enrollment_status(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                enrollment = Enrollment.objects.get(
                    user=request.user,
                    course=obj
                )
                return {
                    'is_enrolled': True,
                    'status': enrollment.status,
                    'progress_percentage': float(enrollment.progress_percentage),
                    'enrolled_at': enrollment.enrolled_at,
                    'last_accessed_at': enrollment.last_accessed_at
                }
            except Enrollment.DoesNotExist:
                return {
                    'is_enrolled': False,
                    'status': None,
                    'progress_percentage': 0.0,
                    'enrolled_at': None,
                    'last_accessed_at': None
                }
        return None
    
    def get_total_lessons(self, obj):
        return Lesson.objects.filter(
            chapter__course=obj,
            is_published=True
        ).count()

class CourseDetailSerializer(CourseSerializer):
    """Detailed course serializer with chapters and lessons"""
    chapters = ChapterSerializer(many=True, read_only=True)
    prerequisites = CourseSerializer(many=True, read_only=True)
    
    class Meta(CourseSerializer.Meta):
        fields = CourseSerializer.Meta.fields + ['chapters', 'prerequisites']

class EnrollmentSerializer(serializers.ModelSerializer):
    """Enrollment serializer"""
    course = CourseSerializer(read_only=True)
    course_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = Enrollment
        fields = [
            'id', 'course', 'course_id', 'status', 'progress_percentage',
            'lessons_completed', 'total_watch_time', 'enrolled_at',
            'started_at', 'completed_at', 'last_accessed_at',
            'certificate_issued', 'certificate_issued_at', 'payment_method'
        ]
        read_only_fields = [
            'id', 'progress_percentage', 'lessons_completed', 'total_watch_time',
            'enrolled_at', 'started_at', 'completed_at', 'last_accessed_at',
            'certificate_issued', 'certificate_issued_at'
        ]
    
    def create(self, validated_data):
        course_id = validated_data.pop('course_id')
        user = self.context['request'].user
        
        try:
            course = Course.objects.get(id=course_id, is_published=True)
        except Course.DoesNotExist:
            raise serializers.ValidationError("Course not found or not published")
        
        # Check if user is already enrolled
        if Enrollment.objects.filter(user=user, course=course).exists():
            raise serializers.ValidationError("User is already enrolled in this course")
        
        # Check access requirements
        if course.requires_subscription and not user.is_subscription_active:
            raise serializers.ValidationError("Active subscription required for this course")
        
        # Create enrollment
        enrollment = Enrollment.objects.create(
            user=user,
            course=course,
            payment_method='subscription' if course.requires_subscription else 'free',
            **validated_data
        )
        
        return enrollment

class LessonProgressSerializer(serializers.ModelSerializer):
    """Lesson progress serializer"""
    lesson = LessonSerializer(read_only=True)
    lesson_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = LessonProgress
        fields = [
            'id', 'lesson', 'lesson_id', 'status', 'watch_time',
            'last_position', 'completion_percentage', 'attempts',
            'best_score', 'last_score', 'first_accessed_at',
            'last_accessed_at', 'completed_at'
        ]
        read_only_fields = [
            'id', 'first_accessed_at', 'last_accessed_at', 'completed_at'
        ]
    
    def update(self, instance, validated_data):
        # Auto-mark as completed if completion percentage is high
        if 'completion_percentage' in validated_data:
            completion = float(validated_data['completion_percentage'])
            if completion >= 80 and instance.status != 'completed':
                validated_data['status'] = 'completed'
                validated_data['completed_at'] = timezone.now()
        
        return super().update(instance, validated_data)

class CourseReviewSerializer(serializers.ModelSerializer):
    """Course review serializer"""
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    
    class Meta:
        model = 'CourseReview'  # We'll need to create this model
        fields = [
            'id', 'user_name', 'rating', 'comment', 'created_at'
        ]
        read_only_fields = ['id', 'user_name', 'created_at']

class DashboardSerializer(serializers.Serializer):
    """Dashboard data serializer"""
    user_stats = serializers.DictField()
    continue_learning = EnrollmentSerializer(many=True)
    recommended_courses = CourseSerializer(many=True)
    recent_activity = serializers.ListField()
    upcoming_live_classes = serializers.ListField()