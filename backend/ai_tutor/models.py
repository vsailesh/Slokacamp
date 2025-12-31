from django.db import models
from django.conf import settings
import uuid
import json

class KnowledgeDocument(models.Model):
    """Store uploaded documents for RAG knowledge base"""
    DOCUMENT_TYPE_CHOICES = (
        ('pdf', 'PDF'),
        ('text', 'Text'),
        ('course', 'Course Content'),
        ('sloka', 'Sanskrit Sloka'),
        ('ayurveda', 'Ayurvedic Text'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=500)
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES)
    content = models.TextField()
    source_file = models.FileField(upload_to='knowledge_base/', blank=True, null=True)
    metadata = models.JSONField(default=dict)  # Store additional info like author, language, etc.
    is_active = models.BooleanField(default=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'knowledge_documents'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.document_type})"

class DocumentChunk(models.Model):
    """Store chunked text with embeddings for semantic search"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(KnowledgeDocument, related_name='chunks', on_delete=models.CASCADE)
    chunk_text = models.TextField()
    chunk_index = models.IntegerField()
    embedding = models.JSONField(default=list)  # Store embedding as JSON array
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'document_chunks'
        ordering = ['document', 'chunk_index']
        indexes = [
            models.Index(fields=['document', 'chunk_index']),
        ]
    
    def __str__(self):
        return f"{self.document.title} - Chunk {self.chunk_index}"
    
    def get_embedding(self):
        """Return embedding as numpy array"""
        import numpy as np
        return np.array(self.embedding)
    
    def set_embedding(self, embedding_array):
        """Store numpy array as JSON list"""
        self.embedding = embedding_array.tolist()

class ChatSession(models.Model):
    """Store chat sessions for conversation context"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='ai_chat_sessions', on_delete=models.CASCADE)
    session_id = models.CharField(max_length=100, unique=True)
    context_type = models.CharField(max_length=50, default='general')  # general, course, payment, etc.
    context_data = models.JSONField(default=dict)  # Store context like course_id, lesson_id, etc.
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'chat_sessions'
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.session_id}"

class ChatMessage(models.Model):
    """Store individual chat messages for history"""
    ROLE_CHOICES = (
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(ChatSession, related_name='messages', on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    tool_calls = models.JSONField(default=list, blank=True)  # Store function calls made by AI
    metadata = models.JSONField(default=dict)  # Store additional info like tokens used, response time, etc.
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'chat_messages'
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."

class AIToolUsage(models.Model):
    """Track MCP tool usage for analytics and debugging"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(ChatSession, related_name='tool_usage', on_delete=models.CASCADE)
    message = models.ForeignKey(ChatMessage, related_name='tool_executions', on_delete=models.CASCADE, null=True)
    tool_name = models.CharField(max_length=100)
    tool_input = models.JSONField()
    tool_output = models.JSONField()
    execution_time_ms = models.IntegerField()
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ai_tool_usage'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.tool_name} - {'Success' if self.success else 'Failed'}"

class QuizQuestion(models.Model):
    """Store AI-generated quiz questions"""
    DIFFICULTY_CHOICES = (
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey('courses.Course', related_name='ai_quizzes', on_delete=models.CASCADE, null=True, blank=True)
    lesson = models.ForeignKey('courses.Lesson', related_name='ai_quizzes', on_delete=models.CASCADE, null=True, blank=True)
    question_text = models.TextField()
    options = models.JSONField()  # List of options
    correct_answer = models.CharField(max_length=500)
    explanation = models.TextField()
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='medium')
    topic = models.CharField(max_length=200)
    language = models.CharField(max_length=50, default='english')  # english, sanskrit, hindi
    created_by_ai = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'quiz_questions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.topic} - {self.question_text[:50]}..."
