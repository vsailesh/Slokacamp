"""AI Tutor Service - Main service for AI interactions with MCP integration"""
import json
import asyncio
import logging
from typing import Dict, Any, List, Optional
from django.conf import settings
from .models import ChatSession, ChatMessage, AIToolUsage
from .mcp_tools import MCPTools, MCP_FUNCTION_SCHEMAS, execute_mcp_tool
from .rag_service import rag_service
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class AITutorService:
    """Main AI Tutor service with MCP tool integration"""
    
    def __init__(self):
        self.api_key = os.getenv('EMERGENT_LLM_KEY')
        if not self.api_key:
            logger.warning("EMERGENT_LLM_KEY not found in environment")
    
    def _build_system_message(self, context_type: str = 'general', context_data: Dict = None) -> str:
        """Build context-aware system message"""
        
        base_message = """You are an expert AI Tutor for SlokaCamp, an Ayurvedic and Sanskrit learning platform.

Your capabilities:
- Expert knowledge in Sanskrit slokas, Ayurveda, and traditional Indian wisdom
- Help students with course content, lesson explanations, and practice
- Answer questions about subscriptions, payments, and platform features
- Translate Sanskrit texts and explain their meanings
- Generate practice quizzes and learning exercises
- Provide personalized learning guidance

You have access to tools to:
- Retrieve course information and lesson content
- Check user enrollment and progress
- Access subscription and payment details
- Search the knowledge base for Sanskrit texts and Ayurvedic content
- List available courses and plans

Guidelines:
- Always be helpful, patient, and encouraging
- Use clear, simple language when explaining complex concepts
- Provide examples and context when teaching
- If you don't know something, admit it and offer to help find the information
- Use your tools to access real-time data about courses, enrollments, and content
- For Sanskrit translations, explain both literal and contextual meanings
- When discussing Ayurveda, cite traditional sources when possible"""

        # Add context-specific instructions
        if context_type == 'course' and context_data:
            course_id = context_data.get('course_id')
            if course_id:
                base_message += f"\n\nCONTEXT: User is currently viewing course (ID: {course_id}). Focus on helping with this course content."
        
        elif context_type == 'lesson' and context_data:
            lesson_id = context_data.get('lesson_id')
            if lesson_id:
                base_message += f"\n\nCONTEXT: User is in a lesson (ID: {lesson_id}). Help them understand the lesson content and answer questions."
        
        elif context_type == 'payment' and context_data:
            base_message += "\n\nCONTEXT: User is viewing subscription/payment information. Help them understand plans and pricing."
        
        return base_message
    
    async def chat(self, 
                   user_id: str,
                   message: str,
                   session_id: str,
                   context_type: str = 'general',
                   context_data: Optional[Dict] = None,
                   use_rag: bool = True) -> Dict[str, Any]:
        """
        Main chat method with MCP tool integration
        
        Args:
            user_id: User ID
            message: User message
            session_id: Chat session ID
            context_type: Type of context (general, course, lesson, payment)
            context_data: Additional context data (course_id, lesson_id, etc.)
            use_rag: Whether to use RAG for knowledge retrieval
        
        Returns:
            Dict with response, tool_calls, and metadata
        """
        try:
            from emergentintegrations.llm.chat import LlmChat, UserMessage
            
            # Get or create chat session
            from accounts.models import User
            user = User.objects.get(id=user_id)
            
            chat_session, created = ChatSession.objects.get_or_create(
                session_id=session_id,
                user=user,
                defaults={
                    'context_type': context_type,
                    'context_data': context_data or {}
                }
            )
            
            # Update context if changed
            if not created:
                chat_session.context_type = context_type
                chat_session.context_data = context_data or {}
                chat_session.save()
            
            # Save user message
            ChatMessage.objects.create(
                session=chat_session,
                role='user',
                content=message
            )
            
            # Build system message
            system_message = self._build_system_message(context_type, context_data)
            
            # RAG: Search knowledge base if enabled
            rag_context = ""
            if use_rag:
                rag_results = rag_service.search_knowledge_base(
                    query=message,
                    top_k=3,
                    document_types=['sloka', 'ayurveda', 'course'] if context_type in ['course', 'lesson'] else None
                )
                
                if rag_results:
                    rag_context = "\n\nRELEVANT KNOWLEDGE BASE:\n" + rag_service.build_context_from_results(rag_results)
                    system_message += rag_context
            
            # Get chat history (last 10 messages)
            history_messages = ChatMessage.objects.filter(
                session=chat_session
            ).order_by('-created_at')[:10]
            
            # Initialize LLM chat
            llm_chat = LlmChat(
                api_key=self.api_key,
                session_id=session_id,
                system_message=system_message
            ).with_model("openai", "gpt-5.2")
            
            # Build messages array (Note: history is reversed)
            # For now, we'll just use the current message for simplicity
            # In production, you'd want to format the history properly
            
            # Create user message with tool context
            user_msg = UserMessage(text=message)
            
            # First call: Get AI response with potential tool calls
            start_time = datetime.now()
            
            # For function calling, we need to use OpenAI directly
            # emergentintegrations doesn't support function calling yet
            # So we'll use openai library with the emergent key
            
            response_data = await self._call_with_tools(
                message=message,
                system_message=system_message,
                user_id=user_id,
                chat_session=chat_session
            )
            
            end_time = datetime.now()
            response_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            # Save assistant message
            assistant_message = ChatMessage.objects.create(
                session=chat_session,
                role='assistant',
                content=response_data['content'],
                tool_calls=response_data.get('tool_calls', []),
                metadata={
                    'response_time_ms': response_time_ms,
                    'model': 'gpt-5.2',
                    'used_rag': use_rag and len(rag_results) > 0 if use_rag else False,
                }
            )
            
            return {
                'success': True,
                'response': response_data['content'],
                'tool_calls': response_data.get('tool_calls', []),
                'metadata': {
                    'response_time_ms': response_time_ms,
                    'used_rag': use_rag,
                    'session_id': session_id,
                }
            }
        
        except Exception as e:
            logger.error(f"AI chat failed: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'response': "I apologize, but I'm having trouble processing your request right now. Please try again."
            }
    
    async def _call_with_tools(self, 
                               message: str,
                               system_message: str,
                               user_id: str,
                               chat_session: ChatSession) -> Dict[str, Any]:
        """Call OpenAI with function calling support"""
        try:
            import openai
            
            client = openai.AsyncOpenAI(
                api_key=self.api_key,
                base_url="https://api.emergent-ai.workers.dev/v1"
            )
            
            # Build messages
            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": message}
            ]
            
            # First call with tools
            response = await client.chat.completions.create(
                model="gpt-5.2",
                messages=messages,
                tools=MCP_FUNCTION_SCHEMAS,
                tool_choice="auto"
            )
            
            response_message = response.choices[0].message
            tool_calls_data = []
            
            # Check if the model wants to call tools
            if response_message.tool_calls:
                # Execute each tool call
                for tool_call in response_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    logger.info(f"Executing tool: {function_name} with args: {function_args}")
                    
                    # Execute the tool
                    tool_start = datetime.now()
                    tool_result = execute_mcp_tool(function_name, function_args)
                    tool_end = datetime.now()
                    tool_time_ms = int((tool_end - tool_start).total_seconds() * 1000)
                    
                    # Log tool usage
                    AIToolUsage.objects.create(
                        session=chat_session,
                        tool_name=function_name,
                        tool_input=function_args,
                        tool_output=tool_result,
                        execution_time_ms=tool_time_ms,
                        success=tool_result.get('success', False),
                        error_message=tool_result.get('error', '')
                    )
                    
                    tool_calls_data.append({
                        'name': function_name,
                        'arguments': function_args,
                        'result': tool_result
                    })
                    
                    # Add tool result to messages
                    messages.append({
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [{
                            "id": tool_call.id,
                            "type": "function",
                            "function": {
                                "name": function_name,
                                "arguments": json.dumps(function_args)
                            }
                        }]
                    })
                    
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(tool_result)
                    })
                
                # Second call: Get final response with tool results
                final_response = await client.chat.completions.create(
                    model="gpt-5.2",
                    messages=messages
                )
                
                final_content = final_response.choices[0].message.content
                
                return {
                    'content': final_content,
                    'tool_calls': tool_calls_data
                }
            else:
                # No tool calls, return direct response
                return {
                    'content': response_message.content,
                    'tool_calls': []
                }
        
        except Exception as e:
            logger.error(f"Tool calling failed: {e}", exc_info=True)
            # Fallback to simple response
            return {
                'content': f"I apologize, but I encountered an error while processing your request: {str(e)}",
                'tool_calls': []
            }
    
    async def generate_quiz(self, 
                           topic: str,
                           difficulty: str = 'medium',
                           num_questions: int = 5,
                           language: str = 'english') -> Dict[str, Any]:
        """Generate quiz questions on a topic"""
        try:
            from emergentintegrations.llm.chat import LlmChat, UserMessage
            
            prompt = f"""Generate {num_questions} multiple choice quiz questions on the topic: {topic}

Difficulty level: {difficulty}
Language: {language}

For each question, provide:
1. Question text
2. Four options (A, B, C, D)
3. Correct answer
4. Brief explanation

Format as JSON array."""
            
            llm_chat = LlmChat(
                api_key=self.api_key,
                session_id=f"quiz_{datetime.now().timestamp()}",
                system_message="You are an expert quiz generator for Ayurveda and Sanskrit topics."
            ).with_model("openai", "gpt-5.2")
            
            response = await llm_chat.send_message(UserMessage(text=prompt))
            
            return {
                'success': True,
                'quiz': response,
                'topic': topic,
                'difficulty': difficulty,
                'language': language
            }
        
        except Exception as e:
            logger.error(f"Quiz generation failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

# Global instance
ai_tutor_service = AITutorService()
