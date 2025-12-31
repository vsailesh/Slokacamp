from django.contrib import admin
from .models import Device, VideoSession, AuditLog

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('user', 'device_name', 'platform', 'is_active', 'last_accessed', 'created_at')
    list_filter = ('platform', 'is_active', 'created_at')
    search_fields = ('user__email', 'device_name', 'device_id')
    ordering = ('-last_accessed',)
    readonly_fields = ('device_id', 'created_at', 'last_accessed')
    
    actions = ['deactivate_devices', 'activate_devices']
    
    def deactivate_devices(self, request, queryset):
        count = queryset.update(is_active=False)
        self.message_user(request, f'{count} device(s) deactivated.')
    deactivate_devices.short_description = 'Deactivate selected devices'
    
    def activate_devices(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(request, f'{count} device(s) activated.')
    activate_devices.short_description = 'Activate selected devices'

@admin.register(VideoSession)
class VideoSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'lesson', 'device', 'is_active', 'watch_time_seconds', 'started_at', 'expires_at')
    list_filter = ('is_active', 'started_at', 'device__platform')
    search_fields = ('user__email', 'lesson__title', 'session_token')
    ordering = ('-started_at',)
    readonly_fields = ('session_token', 'started_at', 'last_heartbeat')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user', 'device', 'lesson')

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'ip_address', 'created_at')
    list_filter = ('action', 'created_at')
    search_fields = ('user__email', 'ip_address')
    ordering = ('-created_at',)
    readonly_fields = ('user', 'action', 'ip_address', 'user_agent', 'metadata', 'created_at')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
