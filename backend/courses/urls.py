from django.urls import path
from .views import (
    CourseListView, CourseDetailView, EnrollmentCreateView,
    MyEnrollmentsView, LessonProgressView, CourseReviewView
)

app_name = 'courses'

urlpatterns = [
    path('', CourseListView.as_view(), name='course_list'),
    path('<uuid:pk>/', CourseDetailView.as_view(), name='course_detail'),
    path('enroll/', EnrollmentCreateView.as_view(), name='enroll'),
    path('my-enrollments/', MyEnrollmentsView.as_view(), name='my_enrollments'),
    path('lesson-progress/', LessonProgressView.as_view(), name='lesson_progress'),
    path('<uuid:course_id>/reviews/', CourseReviewView.as_view(), name='course_reviews'),
]
