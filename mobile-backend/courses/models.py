from django.db import models
from django.conf import settings
import uuid
from django.utils import timezone

class Course(models.Model):
    """Ayurveda courses with comprehensive content management"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Basic course information
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=255)
    description = models.TextField()
    short_description = models.CharField(max_length=500, blank=True)
    
    # Course categorization
    category = models.CharField(max_length=50, choices=[
        ('slokas', 'Sanskrit Slokas'),
        ('ayurveda', 'Ayurveda Fundamentals'),
        ('meditation', 'Meditation & Mindfulness'),
        ('yoga', 'Yoga Philosophy'),
        ('astrology', 'Vedic Astrology'),
        ('cooking', 'Ayurvedic Cooking'),
        ('herbs', 'Herbal Medicine'),
        ('lifestyle', 'Ayurvedic Lifestyle'),
    ])
    
    subcategory = models.CharField(max_length=50, blank=True)
    
    # Course level and prerequisites
    level = models.CharField(max_length=20, choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ], default='beginner')
    
    prerequisites = models.ManyToManyField('self', blank=True, symmetrical=False)
    
    # Course content and structure
    thumbnail = models.URLField(blank=True)
    trailer_video = models.URLField(blank=True)
    estimated_duration = models.PositiveIntegerField(help_text='Duration in minutes')
    
    # Instructor information
    instructor_name = models.CharField(max_length=255)
    instructor_bio = models.TextField(blank=True)
    instructor_image = models.URLField(blank=True)
    instructor_credentials = models.JSONField(default=list, blank=True)
    
    # Course pricing and access
    is_free = models.BooleanField(default=False)
    requires_subscription = models.BooleanField(default=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    
    # Course status and visibility
    is_published = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    
    # SEO and marketing
    meta_description = models.CharField(max_length=160, blank=True)
    keywords = models.JSONField(default=list, blank=True)
    
    # Analytics and ratings
    view_count = models.PositiveIntegerField(default=0)
    enrollment_count = models.PositiveIntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_ratings = models.PositiveIntegerField(default=0)
    
    # Course learning outcomes
    learning_objectives = models.JSONField(default=list, blank=True)
    skills_gained = models.JSONField(default=list, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'courses'
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category', 'level']),
            models.Index(fields=['is_published', 'is_featured']),
            models.Index(fields=['-average_rating']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if self.is_published and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

class Chapter(models.Model):
    """Course chapters for organizing lessons"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='chapters')
    
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField()
    
    # Chapter status
    is_published = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'course_chapters'
        verbose_name = 'Chapter'
        verbose_name_plural = 'Chapters'
        ordering = ['course', 'order']
        unique_together = [['course', 'order']]
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"

class Lesson(models.Model):
    """Individual lessons within chapters"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='lessons')
    
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField()
    
    # Lesson content type
    content_type = models.CharField(max_length=20, choices=[
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('text', 'Text/Article'),
        ('interactive', 'Interactive Exercise'),
        ('quiz', 'Quiz'),
        ('assignment', 'Assignment'),
    ])
    
    # Lesson duration and difficulty
    duration = models.PositiveIntegerField(help_text='Duration in seconds')
    difficulty = models.CharField(max_length=20, choices=[
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ], default='medium')
    
    # Content references
    video_id = models.CharField(max_length=255, blank=True)
    audio_file_url = models.URLField(blank=True)
    text_content = models.TextField(blank=True)
    
    # Lesson resources and materials
    resources = models.JSONField(default=list, blank=True)  # Links to PDFs, images, etc.
    transcript = models.TextField(blank=True)
    
    # Sanskrit-specific content
    sanskrit_text = models.TextField(blank=True)
    transliteration = models.TextField(blank=True)
    translation = models.TextField(blank=True)
    
    # Lesson status and access
    is_published = models.BooleanField(default=True)
    is_preview = models.BooleanField(default=False)  # Free preview lesson
    requires_completion_of_previous = models.BooleanField(default=True)
    
    # Analytics
    view_count = models.PositiveIntegerField(default=0)
    completion_count = models.PositiveIntegerField(default=0)
    average_completion_time = models.PositiveIntegerField(default=0, help_text='Average time to complete in seconds')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'course_lessons'
        verbose_name = 'Lesson'
        verbose_name_plural = 'Lessons'
        ordering = ['chapter', 'order']
        unique_together = [['chapter', 'order']]
    
    def __str__(self):
        return f"{self.chapter.course.title} - {self.chapter.title} - {self.title}"
    
    @property
    def course(self):
        return self.chapter.course

class Enrollment(models.Model):
    """User course enrollments and progress tracking"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    
    # Enrollment status
    status = models.CharField(max_length=20, choices=[
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('paused', 'Paused'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ], default='active')
    
    # Progress tracking
    progress_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    lessons_completed = models.PositiveIntegerField(default=0)
    total_watch_time = models.PositiveIntegerField(default=0)  # in seconds
    
    # Enrollment dates
    enrolled_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    last_accessed_at = models.DateTimeField(blank=True, null=True)
    
    # Certificate and achievements
    certificate_issued = models.BooleanField(default=False)
    certificate_issued_at = models.DateTimeField(blank=True, null=True)
    
    # Payment information
    payment_method = models.CharField(max_length=50, choices=[
        ('free', 'Free'),
        ('subscription', 'Subscription'),
        ('one_time', 'One-time Purchase'),
    ], default='subscription')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'course_enrollments'
        verbose_name = 'Enrollment'
        verbose_name_plural = 'Enrollments'
        unique_together = [['user', 'course']]
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['course', 'status']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.course.title}"

class LessonProgress(models.Model):
    """Detailed lesson progress and completion tracking"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='progress_records')
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='lesson_progress')
    
    # Progress details
    status = models.CharField(max_length=20, choices=[
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('skipped', 'Skipped'),
    ], default='not_started')
    
    # Watch time and position
    watch_time = models.PositiveIntegerField(default=0)  # Total watch time in seconds
    last_position = models.PositiveIntegerField(default=0)  # Last playback position in seconds
    completion_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    
    # Attempt and score tracking (for quizzes/assignments)
    attempts = models.PositiveIntegerField(default=0)
    best_score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    last_score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    
    # Timestamps
    first_accessed_at = models.DateTimeField(auto_now_add=True)
    last_accessed_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'lesson_progress'
        verbose_name = 'Lesson Progress'
        verbose_name_plural = 'Lesson Progress'
        unique_together = [['user', 'lesson']]
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['lesson', 'status']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.lesson.title} ({self.status})"