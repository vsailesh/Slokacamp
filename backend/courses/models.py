from django.db import models
from django.conf import settings
import uuid

class Course(models.Model):
    DIFFICULTY_CHOICES = (
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    short_description = models.CharField(max_length=500)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='beginner')
    duration_hours = models.IntegerField(default=0)
    category = models.CharField(max_length=100)
    instructor_name = models.CharField(max_length=255)
    instructor_bio = models.TextField(blank=True)
    instructor_image = models.URLField(blank=True)
    thumbnail_image = models.URLField(blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    total_reviews = models.IntegerField(default=0)
    total_students = models.IntegerField(default=0)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'courses'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class Lesson(models.Model):
    LESSON_TYPE_CHOICES = (
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('text', 'Text'),
        ('practice', 'Practice'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, related_name='lessons', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    lesson_type = models.CharField(max_length=20, choices=LESSON_TYPE_CHOICES, default='video')
    order = models.IntegerField(default=0)
    duration_minutes = models.IntegerField(default=0)
    video_url = models.URLField(blank=True)
    audio_url = models.URLField(blank=True)
    transcript = models.TextField(blank=True)
    xp_reward = models.IntegerField(default=10)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'lessons'
        ordering = ['course', 'order']

    def __str__(self):
        return f"{self.course.title} - {self.title}"

class Enrollment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='enrollments', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name='enrollments', on_delete=models.CASCADE)
    progress_percentage = models.IntegerField(default=0)
    completed_lessons = models.IntegerField(default=0)
    total_lessons = models.IntegerField(default=0)
    last_accessed = models.DateTimeField(auto_now=True)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'enrollments'
        unique_together = ('user', 'course')

    def __str__(self):
        return f"{self.user.email} - {self.course.title}"

class LessonProgress(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='lesson_progress', on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, related_name='progress', on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    completion_percentage = models.IntegerField(default=0)
    time_spent_seconds = models.IntegerField(default=0)
    last_position_seconds = models.IntegerField(default=0)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'lesson_progress'
        unique_together = ('user', 'lesson')

    def __str__(self):
        return f"{self.user.email} - {self.lesson.title}"

class Review(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='reviews', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name='reviews', on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'reviews'
        unique_together = ('user', 'course')

    def __str__(self):
        return f"{self.user.email} - {self.course.title} - {self.rating}/5"
