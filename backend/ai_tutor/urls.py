from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    KnowledgeDocumentViewSet, ChatSessionViewSet,
    chat_api, explain_sloka_api, generate_quiz_api,
    translate_sanskrit_api, search_knowledge_base_api
)

router = DefaultRouter()
router.register(r'documents', KnowledgeDocumentViewSet, basename='document')
router.register(r'sessions', ChatSessionViewSet, basename='session')

urlpatterns = [
    path('', include(router.urls)),
    path('chat/', chat_api, name='ai-chat'),
    path('explain-sloka/', explain_sloka_api, name='explain-sloka'),
    path('quiz/', generate_quiz_api, name='generate-quiz'),
    path('translate/', translate_sanskrit_api, name='translate-sanskrit'),
    path('search/', search_knowledge_base_api, name='search-knowledge-base'),
]
