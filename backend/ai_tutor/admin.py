from django.contrib import admin
from .models import (
    KnowledgeDocument, DocumentChunk, ChatSession, 
    ChatMessage, AIToolUsage, QuizQuestion
)

@admin.register(KnowledgeDocument)
class KnowledgeDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'document_type', 'is_active', 'uploaded_by', 'created_at')
    list_filter = ('document_type', 'is_active', 'created_at')
    search_fields = ('title', 'content')
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Document Info', {
            'fields': ('title', 'document_type', 'content', 'source_file', 'is_active')
        }),
        ('Metadata', {
            'fields': ('metadata', 'uploaded_by')
        }),
        ('Timestamps', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(DocumentChunk)
class DocumentChunkAdmin(admin.ModelAdmin):
    list_display = ('document', 'chunk_index', 'created_at')
    list_filter = ('document', 'created_at')
    search_fields = ('chunk_text',)
    readonly_fields = ('id', 'created_at')
    
    def has_add_permission(self, request):
        # Chunks are created automatically
        return False

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'session_id', 'context_type', 'created_at', 'updated_at')
    list_filter = ('context_type', 'created_at')
    search_fields = ('user__email', 'session_id')
    readonly_fields = ('id', 'created_at', 'updated_at')

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('session', 'role', 'content_preview', 'created_at')
    list_filter = ('role', 'created_at')
    search_fields = ('content',)
    readonly_fields = ('id', 'created_at')
    
    def content_preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content'

@admin.register(AIToolUsage)
class AIToolUsageAdmin(admin.ModelAdmin):
    list_display = ('tool_name', 'session', 'success', 'execution_time_ms', 'created_at')
    list_filter = ('tool_name', 'success', 'created_at')
    search_fields = ('tool_name', 'error_message')
    readonly_fields = ('id', 'created_at')

@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    list_display = ('topic', 'difficulty', 'language', 'course', 'created_at')
    list_filter = ('difficulty', 'language', 'created_by_ai', 'created_at')
    search_fields = ('question_text', 'topic')
    readonly_fields = ('id', 'created_at')
