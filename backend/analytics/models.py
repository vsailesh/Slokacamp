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
