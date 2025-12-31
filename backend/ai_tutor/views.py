from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from .models import (
    KnowledgeDocument, DocumentChunk, ChatSession, 
    ChatMessage, AIToolUsage, QuizQuestion
)
from .serializers import (
    KnowledgeDocumentSerializer, DocumentChunkSerializer,
    ChatSessionSerializer, ChatMessageSerializer, AIToolUsageSerializer,
    QuizQuestionSerializer, ChatRequestSerializer, ChatResponseSerializer,
    QuizGenerationRequestSerializer, DocumentUploadSerializer
)
from .ai_service import ai_tutor_service
from .rag_service import rag_service
import asyncio
import logging
import uuid
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None
import io

logger = logging.getLogger(__name__)

class KnowledgeDocumentViewSet(viewsets.ModelViewSet):
    """Admin viewset for managing knowledge documents"""
    queryset = KnowledgeDocument.objects.all()
    serializer_class = KnowledgeDocumentSerializer
    permission_classes = [IsAdminUser]
    
    def perform_create(self, serializer):
        document = serializer.save(uploaded_by=self.request.user)
        
        # Process document in background (generate embeddings)
        try:
            chunks_created = rag_service.process_document(document)
            logger.info(f"Processed document {document.title}: {chunks_created} chunks created")
        except Exception as e:
            logger.error(f"Failed to process document: {e}")
    
    @action(detail=True, methods=['post'])
    def reprocess(self, request, pk=None):
        """Reprocess document to regenerate embeddings"""
        document = self.get_object()
        try:
            chunks_created = rag_service.process_document(document)
            return Response({
                'success': True,
                'message': f'Document reprocessed successfully',
                'chunks_created': chunks_created
            })
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_pdf(self, request):
        """Upload and process PDF document"""
        serializer = DocumentUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            data = serializer.validated_data
            file_obj = data.get('file')
            
            # Extract text from PDF if file provided
            content = data.get('content', '')
            if file_obj and file_obj.name.endswith('.pdf'):
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_obj.read()))
                text_parts = []
                for page in pdf_reader.pages:
                    text_parts.append(page.extract_text())
                content = '\n\n'.join(text_parts)
            
            # Create document
            document = KnowledgeDocument.objects.create(
                title=data['title'],
                document_type=data['document_type'],
                content=content,
                source_file=file_obj,
                metadata=data.get('metadata', {}),
                uploaded_by=request.user
            )
            
            # Process document
            chunks_created = rag_service.process_document(document)
            
            return Response({
                'success': True,
                'document': KnowledgeDocumentSerializer(document).data,
                'chunks_created': chunks_created
            }, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            logger.error(f"PDF upload failed: {e}", exc_info=True)
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ChatSessionViewSet(viewsets.ReadOnlyModelViewSet):
    """Viewset for viewing chat sessions"""
    serializer_class = ChatSessionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Users can only see their own sessions
        if self.request.user.is_staff:
            return ChatSession.objects.all()
        return ChatSession.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """Get all messages in a session"""
        session = self.get_object()
        messages = session.messages.all().order_by('created_at')
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def tool_usage(self, request, pk=None):
        """Get tool usage analytics for a session"""
        session = self.get_object()
        tool_usage = session.tool_usage.all()
        serializer = AIToolUsageSerializer(tool_usage, many=True)
        return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chat_api(request):
    """
    Main AI chat endpoint
    
    POST /api/ai/chat/
    {
        "message": "User question",
        "session_id": "optional-session-id",
        "context_type": "general|course|lesson|payment",
        "context_data": {
            "course_id": "uuid",
            "lesson_id": "uuid"
        },
        "use_rag": true
    }
    """
    serializer = ChatRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    
    # Generate session ID if not provided
    session_id = data.get('session_id') or f"session_{request.user.id}_{uuid.uuid4().hex[:8]}"
    
    try:
        # Call AI service (async)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            ai_tutor_service.chat(
                user_id=str(request.user.id),
                message=data['message'],
                session_id=session_id,
                context_type=data.get('context_type', 'general'),
                context_data=data.get('context_data', {}),
                use_rag=data.get('use_rag', True)
            )
        )
        loop.close()
        
        # Add session_id to response
        result['session_id'] = session_id
        
        response_serializer = ChatResponseSerializer(data=result)
        if response_serializer.is_valid():
            return Response(response_serializer.data)
        
        return Response(result)
    
    except Exception as e:
        logger.error(f"Chat API error: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e),
            'response': "I apologize, but I encountered an error. Please try again."
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def explain_sloka_api(request):
    """
    Explain a Sanskrit sloka
    
    POST /api/ai/explain-sloka/
    {
        "sloka": "Sanskrit text",
        "include_translation": true,
        "include_context": true
    }
    """
    sloka = request.data.get('sloka')
    if not sloka:
        return Response({
            'success': False,
            'error': 'Sloka text is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    include_translation = request.data.get('include_translation', True)
    include_context = request.data.get('include_context', True)
    
    # Build detailed prompt
    prompt = f"""Please explain this Sanskrit sloka:

{sloka}

"""
    if include_translation:
        prompt += "- Provide word-by-word translation\n- Provide complete English translation\n"
    
    if include_context:
        prompt += "- Explain the philosophical or spiritual context\n- Share relevant insights from traditional teachings\n"
    
    session_id = f"sloka_{request.user.id}_{uuid.uuid4().hex[:8]}"
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            ai_tutor_service.chat(
                user_id=str(request.user.id),
                message=prompt,
                session_id=session_id,
                context_type='sloka',
                context_data={'sloka': sloka},
                use_rag=True  # Use RAG to find similar slokas
            )
        )
        loop.close()
        
        return Response(result)
    
    except Exception as e:
        logger.error(f"Sloka explanation error: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_quiz_api(request):
    """
    Generate quiz questions
    
    POST /api/ai/quiz/
    {
        "topic": "Ayurvedic doshas",
        "difficulty": "medium",
        "num_questions": 5,
        "language": "english"
    }
    """
    serializer = QuizGenerationRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            ai_tutor_service.generate_quiz(
                topic=data['topic'],
                difficulty=data['difficulty'],
                num_questions=data['num_questions'],
                language=data['language']
            )
        )
        loop.close()
        
        return Response(result)
    
    except Exception as e:
        logger.error(f"Quiz generation error: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def translate_sanskrit_api(request):
    """
    Translate Sanskrit text
    
    POST /api/ai/translate/
    {
        "text": "Sanskrit text",
        "target_language": "english"
    }
    """
    text = request.data.get('text')
    target_language = request.data.get('target_language', 'english')
    
    if not text:
        return Response({
            'success': False,
            'error': 'Text is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    prompt = f"Translate this Sanskrit text to {target_language}:\n\n{text}\n\nProvide both literal and contextual translation."
    
    session_id = f"translate_{request.user.id}_{uuid.uuid4().hex[:8]}"
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            ai_tutor_service.chat(
                user_id=str(request.user.id),
                message=prompt,
                session_id=session_id,
                context_type='translation',
                context_data={'text': text, 'target_language': target_language},
                use_rag=True
            )
        )
        loop.close()
        
        return Response(result)
    
    except Exception as e:
        logger.error(f"Translation error: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_knowledge_base_api(request):
    """
    Search knowledge base
    
    GET /api/ai/search/?query=ayurveda&top_k=5
    """
    query = request.query_params.get('query')
    top_k = int(request.query_params.get('top_k', 5))
    
    if not query:
        return Response({
            'success': False,
            'error': 'Query parameter is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        results = rag_service.search_knowledge_base(query, top_k=top_k)
        return Response({
            'success': True,
            'query': query,
            'results': results
        })
    
    except Exception as e:
        logger.error(f"Knowledge base search error: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
