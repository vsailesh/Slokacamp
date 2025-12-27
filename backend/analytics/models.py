from django.db import models
from django.conf import settings
import uuid

class UserActivity(models.Model):
    ACTIVITY_TYPES = (
        ('login', 'Login'),
        ('lesson_complete', 'Lesson Complete'),
        ('course_enroll', 'Course Enroll'),
        ('course_complete', 'Course Complete'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='activities', on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPES)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_activities'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.activity_type}"


class Discussion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='discussions', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()
    course = models.ForeignKey('courses.Course', related_name='discussions', on_delete=models.SET_NULL, null=True, blank=True)
    views = models.IntegerField(default=0)
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'discussions'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class DiscussionReply(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    discussion = models.ForeignKey(Discussion, related_name='replies', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='discussion_replies', on_delete=models.CASCADE)
    content = models.TextField()
    is_accepted = models.BooleanField(default=False)
    upvotes = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'discussion_replies'
        ordering = ['created_at']

    def __str__(self):
        return f"Reply to {self.discussion.title} by {self.user.email}"
