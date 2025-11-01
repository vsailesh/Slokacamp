from django.contrib import admin
from .models import UserActivity

@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity_type', 'created_at')
    list_filter = ('activity_type', 'created_at')
    search_fields = ('user__email',)
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
