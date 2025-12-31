from rest_framework import serializers
from .models import (
    KnowledgeDocument, DocumentChunk, ChatSession, 
    ChatMessage, AIToolUsage, QuizQuestion
)

class KnowledgeDocumentSerializer(serializers.ModelSerializer):
    chunks_count = serializers.SerializerMethodField()
    
    class Meta:
        model = KnowledgeDocument
        fields = [
            'id', 'title', 'document_type', 'content', 'source_file',
            'metadata', 'is_active', 'chunks_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_chunks_count(self, obj):
        return obj.chunks.count()

class DocumentChunkSerializer(serializers.ModelSerializer):
    document_title = serializers.CharField(source='document.title', read_only=True)
    
    class Meta:
        model = DocumentChunk
        fields = ['id', 'document', 'document_title', 'chunk_text', 'chunk_index', 'metadata', 'created_at']
        read_only_fields = ['id', 'created_at']

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['id', 'role', 'content', 'tool_calls', 'metadata', 'created_at']
        read_only_fields = ['id', 'created_at']

class ChatSessionSerializer(serializers.ModelSerializer):
    messages = ChatMessageSerializer(many=True, read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = ChatSession
        fields = [
            'id', 'user', 'user_email', 'session_id', 'context_type',
            'context_data', 'messages', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class AIToolUsageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIToolUsage
        fields = [
            'id', 'tool_name', 'tool_input', 'tool_output',
            'execution_time_ms', 'success', 'error_message', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class QuizQuestionSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)
    
    class Meta:
        model = QuizQuestion
        fields = [
            'id', 'course', 'course_title', 'lesson', 'lesson_title',
            'question_text', 'options', 'correct_answer', 'explanation',
            'difficulty', 'topic', 'language', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

# Request/Response Serializers
class ChatRequestSerializer(serializers.Serializer):
    message = serializers.CharField(required=True)
    session_id = serializers.CharField(required=False)
    context_type = serializers.CharField(default='general')
    context_data = serializers.JSONField(required=False, default=dict)
    use_rag = serializers.BooleanField(default=True)

class ChatResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    response = serializers.CharField()
    tool_calls = serializers.ListField(required=False)
    metadata = serializers.JSONField(required=False)
    session_id = serializers.CharField(required=False)
    error = serializers.CharField(required=False)

class QuizGenerationRequestSerializer(serializers.Serializer):
    topic = serializers.CharField(required=True)
    difficulty = serializers.ChoiceField(
        choices=['easy', 'medium', 'hard'],
        default='medium'
    )
    num_questions = serializers.IntegerField(default=5, min_value=1, max_value=20)
    language = serializers.ChoiceField(
        choices=['english', 'sanskrit', 'hindi'],
        default='english'
    )

class DocumentUploadSerializer(serializers.Serializer):
    title = serializers.CharField(required=True)
    document_type = serializers.ChoiceField(
        choices=['pdf', 'text', 'course', 'sloka', 'ayurveda'],
        required=True
    )
    content = serializers.CharField(required=False, allow_blank=True)
    file = serializers.FileField(required=False)
    metadata = serializers.JSONField(required=False, default=dict)
