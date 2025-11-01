from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from .models import Course, Lesson, Enrollment, LessonProgress, Review
from .serializers import (
    CourseSerializer, CourseDetailSerializer, LessonSerializer,
    EnrollmentSerializer, LessonProgressSerializer, ReviewSerializer
)

class CourseListView(generics.ListAPIView):
    queryset = Course.objects.filter(is_published=True)
    serializer_class = CourseSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.query_params.get('category', None)
        difficulty = self.request.query_params.get('difficulty', None)
        search = self.request.query_params.get('search', None)
        
        if category:
            queryset = queryset.filter(category__iexact=category)
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )
        
        return queryset

class CourseDetailView(generics.RetrieveAPIView):
    queryset = Course.objects.filter(is_published=True)
    serializer_class = CourseDetailSerializer
    permission_classes = [permissions.AllowAny]

class EnrollmentCreateView(generics.CreateAPIView):
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        course_id = serializer.validated_data['course_id']
        course = Course.objects.get(id=course_id)
        total_lessons = course.lessons.filter(is_published=True).count()
        serializer.save(user=self.request.user, course=course, total_lessons=total_lessons)

class MyEnrollmentsView(generics.ListAPIView):
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Enrollment.objects.filter(user=self.request.user)

class LessonProgressView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = LessonProgressSerializer(data=request.data)
        if serializer.is_valid():
            lesson_id = serializer.validated_data['lesson_id']
            lesson = Lesson.objects.get(id=lesson_id)
            
            progress, created = LessonProgress.objects.update_or_create(
                user=request.user,
                lesson=lesson,
                defaults=serializer.validated_data
            )
            
            # Update enrollment progress
            enrollment = Enrollment.objects.filter(
                user=request.user,
                course=lesson.course
            ).first()
            
            if enrollment:
                completed = LessonProgress.objects.filter(
                    user=request.user,
                    lesson__course=lesson.course,
                    is_completed=True
                ).count()
                
                enrollment.completed_lessons = completed
                if enrollment.total_lessons > 0:
                    enrollment.progress_percentage = int((completed / enrollment.total_lessons) * 100)
                enrollment.save()
            
            return Response(LessonProgressSerializer(progress).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CourseReviewView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        course_id = self.kwargs['course_id']
        return Review.objects.filter(course_id=course_id)
    
    def perform_create(self, serializer):
        course_id = self.kwargs['course_id']
        course = Course.objects.get(id=course_id)
        serializer.save(user=self.request.user, course=course)
