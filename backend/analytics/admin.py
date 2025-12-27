from django.contrib import admin
from .models import UserActivity, Discussion, DiscussionReply

@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity_type', 'created_at')
    list_filter = ('activity_type', 'created_at')
    search_fields = ('user__email',)
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)

@admin.register(Discussion)
class DiscussionAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'course', 'views', 'is_resolved', 'created_at')
    list_filter = ('is_resolved', 'created_at', 'course')
    search_fields = ('title', 'content', 'user__email')
    ordering = ('-created_at',)
    readonly_fields = ('views', 'created_at', 'updated_at')

@admin.register(DiscussionReply)
class DiscussionReplyAdmin(admin.ModelAdmin):
    list_display = ('discussion', 'user', 'is_accepted', 'upvotes', 'created_at')
    list_filter = ('is_accepted', 'created_at')
    search_fields = ('content', 'user__email', 'discussion__title')
    ordering = ('-created_at',)
    readonly_fields = ('upvotes', 'created_at', 'updated_at')
