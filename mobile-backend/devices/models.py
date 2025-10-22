from django.db import models
from django.conf import settings
import uuid
from django.utils import timezone

class Device(models.Model):
    """Device registration for single-device playback enforcement"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='devices')
    
    # Device identification
    device_id = models.CharField(max_length=255, unique=True, db_index=True)
    device_name = models.CharField(max_length=255)
    platform = models.CharField(max_length=20, choices=[
        ('ios', 'iOS'),
        ('android', 'Android'),
        ('web', 'Web'),
    ])
    
    # Device info
    os_version = models.CharField(max_length=50, blank=True)
    app_version = models.CharField(max_length=20, blank=True)
    device_model = models.CharField(max_length=100, blank=True)
    
    # Push notifications
    push_token = models.TextField(blank=True, null=True)
    push_token_updated_at = models.DateTimeField(blank=True, null=True)
    
    # Device status
    is_active = models.BooleanField(default=True)
    is_primary = models.BooleanField(default=False)
    
    # Security and tracking
    device_fingerprint = models.JSONField(default=dict, blank=True)
    last_ip_address = models.GenericIPAddressField(blank=True, null=True)
    last_location = models.JSONField(default=dict, blank=True)  # {"country": "", "city": ""}
    
    # Timestamps
    registered_at = models.DateTimeField(auto_now_add=True)
    last_seen_at = models.DateTimeField(auto_now=True)
    deactivated_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'devices'
        verbose_name = 'Device'
        verbose_name_plural = 'Devices'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'is_primary'],
                condition=models.Q(is_primary=True, is_active=True),
                name='unique_primary_device_per_user'
            )
        ]
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['device_id']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.device_name} ({self.platform})"
    
    def deactivate(self):
        """Deactivate the device"""
        self.is_active = False
        self.is_primary = False
        self.deactivated_at = timezone.now()
        self.save(update_fields=['is_active', 'is_primary', 'deactivated_at'])
    
    def make_primary(self):
        """Make this device the primary device for the user"""
        # Deactivate other primary devices for this user
        Device.objects.filter(
            user=self.user,
            is_primary=True,
            is_active=True
        ).exclude(id=self.id).update(
            is_primary=False,
            is_active=False,
            deactivated_at=timezone.now()
        )
        
        self.is_primary = True
        self.is_active = True
        self.deactivated_at = None
        self.save(update_fields=['is_primary', 'is_active', 'deactivated_at'])
    
    @property
    def is_online(self):
        """Check if device was seen recently (within last 5 minutes)"""
        if not self.last_seen_at:
            return False
        return (timezone.now() - self.last_seen_at).seconds < 300

class DeviceTransfer(models.Model):
    """Log device transfers for audit purposes"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    from_device = models.ForeignKey(
        Device, on_delete=models.CASCADE, 
        related_name='transfers_from', 
        null=True, blank=True
    )
    to_device = models.ForeignKey(
        Device, on_delete=models.CASCADE, 
        related_name='transfers_to'
    )
    
    reason = models.CharField(max_length=50, choices=[
        ('new_registration', 'New Device Registration'),
        ('manual_transfer', 'Manual Device Transfer'),
        ('policy_enforcement', 'Policy Enforcement'),
        ('device_lost', 'Device Lost/Stolen'),
    ])
    
    # Audit information
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'device_transfers'
        verbose_name = 'Device Transfer'
        verbose_name_plural = 'Device Transfers'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - Device Transfer ({self.reason})"