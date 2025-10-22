from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

class User(AbstractUser):
    """Extended User model with additional fields for Ayurveda learning platform"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    
    # Profile fields
    profile_picture = models.URLField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    
    # Ayurveda-specific fields
    dosha_type = models.CharField(max_length=20, choices=[
        ('vata', 'Vata'),
        ('pitta', 'Pitta'),
        ('kapha', 'Kapha'),
        ('vata_pitta', 'Vata-Pitta'),
        ('pitta_kapha', 'Pitta-Kapha'),
        ('vata_kapha', 'Vata-Kapha'),
        ('tridosha', 'Tridosha'),
    ], blank=True, null=True)
    
    # Subscription and preferences
    is_premium = models.BooleanField(default=False)
    subscription_end_date = models.DateTimeField(blank=True, null=True)
    preferred_language = models.CharField(max_length=10, default='en')
    
    # Privacy and consent
    has_consented_to_recording = models.BooleanField(default=False)
    recording_consent_date = models.DateTimeField(blank=True, null=True)
    
    # Account verification
    email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=64, blank=True, null=True)
    
    # Social auth providers
    google_id = models.CharField(max_length=100, blank=True, null=True, unique=True)
    facebook_id = models.CharField(max_length=100, blank=True, null=True, unique=True)
    apple_id = models.CharField(max_length=100, blank=True, null=True, unique=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_active = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        db_table = 'auth_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return self.email
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username
    
    @property
    def is_subscription_active(self):
        if not self.subscription_end_date:
            return False
        from django.utils import timezone
        return self.subscription_end_date > timezone.now()

class UserProfile(models.Model):
    """Additional user profile information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Learning preferences
    learning_goals = models.JSONField(default=list, blank=True)
    experience_level = models.CharField(max_length=20, choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ], default='beginner')
    
    # Health information (optional, for personalized Ayurvedic recommendations)
    health_conditions = models.JSONField(default=list, blank=True)
    dietary_preferences = models.JSONField(default=list, blank=True)
    
    # Progress tracking
    total_watch_time = models.PositiveIntegerField(default=0)  # in seconds
    courses_completed = models.PositiveIntegerField(default=0)
    streak_days = models.PositiveIntegerField(default=0)
    last_activity_date = models.DateField(blank=True, null=True)
    
    # Notifications preferences
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    weekly_digest = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"{self.user.email} - Profile"