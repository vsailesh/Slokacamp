from rest_framework import serializers
from .models import Course, Lesson, Enrollment, LessonProgress, Review
from accounts.serializers import UserSerializer

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'

class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ('user',)

class CourseSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = '__all__'
    
    def get_lessons_count(self, obj):
        return obj.lessons.filter(is_published=True).count()

class CourseDetailSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    lessons_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = '__all__'
    
    def get_lessons_count(self, obj):
        return obj.lessons.filter(is_published=True).count()

class EnrollmentSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    course_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = Enrollment
        fields = '__all__'
        read_only_fields = ('user', 'progress_percentage', 'completed_lessons', 'total_lessons')

class LessonProgressSerializer(serializers.ModelSerializer):
    lesson = LessonSerializer(read_only=True)
    lesson_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = LessonProgress
        fields = '__all__'
        read_only_fields = ('user',)
