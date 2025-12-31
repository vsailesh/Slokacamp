"""MCP Tools - Functions that the AI can call to access app data and perform actions"""
import json
from typing import Dict, Any, List
from django.conf import settings
from courses.models import Course, Lesson, Enrollment, LessonProgress
from payments.models import Subscription, SubscriptionPlan
from accounts.models import User
from datetime import datetime

class MCPTools:
    """Collection of tools that AI can use via function calling"""
    
    @staticmethod
    def get_course_info(course_id: str) -> Dict[str, Any]:
        """Get detailed information about a course"""
        try:
            course = Course.objects.get(id=course_id)
            lessons = course.lessons.filter(is_published=True).order_by('order')
            
            return {
                'success': True,
                'course': {
                    'id': str(course.id),
                    'title': course.title,
                    'description': course.description,
                    'difficulty': course.difficulty,
                    'duration_hours': course.duration_hours,
                    'category': course.category,
                    'instructor': {
                        'name': course.instructor_name,
                        'bio': course.instructor_bio,
                    },
                    'rating': float(course.rating),
                    'total_students': course.total_students,
                    'lessons_count': lessons.count(),
                    'lessons': [
                        {
                            'id': str(lesson.id),
                            'title': lesson.title,
                            'lesson_type': lesson.lesson_type,
                            'duration_minutes': lesson.duration_minutes,
                            'order': lesson.order,
                        }
                        for lesson in lessons[:10]  # First 10 lessons
                    ]
                }
            }
        except Course.DoesNotExist:
            return {'success': False, 'error': 'Course not found'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def get_user_enrollment_status(user_id: str, course_id: str = None) -> Dict[str, Any]:
        """Get user's enrollment status and progress"""
        try:
            user = User.objects.get(id=user_id)
            
            if course_id:
                # Get specific course enrollment
                enrollment = Enrollment.objects.filter(
                    user=user, course_id=course_id
                ).first()
                
                if not enrollment:
                    return {
                        'success': True,
                        'enrolled': False,
                        'message': 'User is not enrolled in this course'
                    }
                
                return {
                    'success': True,
                    'enrolled': True,
                    'progress_percentage': enrollment.progress_percentage,
                    'completed_lessons': enrollment.completed_lessons,
                    'total_lessons': enrollment.total_lessons,
                    'last_accessed': enrollment.last_accessed.isoformat(),
                    'enrolled_at': enrollment.enrolled_at.isoformat(),
                }
            else:
                # Get all enrollments
                enrollments = Enrollment.objects.filter(user=user)
                return {
                    'success': True,
                    'total_enrollments': enrollments.count(),
                    'courses': [
                        {
                            'course_id': str(e.course.id),
                            'course_title': e.course.title,
                            'progress': e.progress_percentage,
                            'last_accessed': e.last_accessed.isoformat(),
                        }
                        for e in enrollments
                    ]
                }
        except User.DoesNotExist:
            return {'success': False, 'error': 'User not found'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def get_subscription_status(user_id: str) -> Dict[str, Any]:
        """Get user's subscription status and details"""
        try:
            user = User.objects.get(id=user_id)
            subscription = Subscription.objects.filter(user=user).first()
            
            if not subscription:
                return {
                    'success': True,
                    'has_subscription': False,
                    'message': 'User has no active subscription'
                }
            
            return {
                'success': True,
                'has_subscription': True,
                'status': subscription.status,
                'plan_name': subscription.plan.name,
                'plan_type': subscription.plan.plan_type,
                'price': float(subscription.plan.price),
                'current_period_start': subscription.current_period_start.isoformat() if subscription.current_period_start else None,
                'current_period_end': subscription.current_period_end.isoformat() if subscription.current_period_end else None,
                'cancel_at_period_end': subscription.cancel_at_period_end,
                'trial_end': subscription.trial_end.isoformat() if subscription.trial_end else None,
            }
        except User.DoesNotExist:
            return {'success': False, 'error': 'User not found'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def get_lesson_content(lesson_id: str) -> Dict[str, Any]:
        """Get lesson content including transcript"""
        try:
            lesson = Lesson.objects.get(id=lesson_id)
            
            return {
                'success': True,
                'lesson': {
                    'id': str(lesson.id),
                    'title': lesson.title,
                    'description': lesson.description,
                    'lesson_type': lesson.lesson_type,
                    'duration_minutes': lesson.duration_minutes,
                    'transcript': lesson.transcript,
                    'course_title': lesson.course.title,
                    'xp_reward': lesson.xp_reward,
                }
            }
        except Lesson.DoesNotExist:
            return {'success': False, 'error': 'Lesson not found'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def list_available_courses(category: str = None, difficulty: str = None) -> Dict[str, Any]:
        """List available courses with optional filters"""
        try:
            courses = Course.objects.filter(is_published=True)
            
            if category:
                courses = courses.filter(category__icontains=category)
            if difficulty:
                courses = courses.filter(difficulty=difficulty)
            
            return {
                'success': True,
                'total_courses': courses.count(),
                'courses': [
                    {
                        'id': str(course.id),
                        'title': course.title,
                        'short_description': course.short_description,
                        'difficulty': course.difficulty,
                        'duration_hours': course.duration_hours,
                        'category': course.category,
                        'rating': float(course.rating),
                        'total_students': course.total_students,
                    }
                    for course in courses[:20]  # Limit to 20 courses
                ]
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def translate_sanskrit(text: str, target_language: str = 'english') -> Dict[str, Any]:
        """Translate Sanskrit text (simplified version - would need actual translation API)"""
        # This is a placeholder - in production, you'd use a real Sanskrit translation API
        # or integrate with the LLM to do the translation
        return {
            'success': True,
            'original': text,
            'translated': f"[Translation to {target_language} would appear here]",
            'language': target_language,
            'note': 'This is a placeholder. Integration with Sanskrit translation API or LLM needed.'
        }
    
    @staticmethod
    def get_payment_plans() -> Dict[str, Any]:
        """Get available subscription plans"""
        try:
            plans = SubscriptionPlan.objects.filter(is_active=True)
            
            return {
                'success': True,
                'plans': [
                    {
                        'id': str(plan.id),
                        'name': plan.name,
                        'description': plan.description,
                        'plan_type': plan.plan_type,
                        'price': float(plan.price),
                        'trial_days': plan.trial_days,
                        'features': plan.features,
                    }
                    for plan in plans
                ]
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

# Define function schemas for GPT function calling
MCP_FUNCTION_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "get_course_info",
            "description": "Get detailed information about a specific course including lessons, instructor, and ratings",
            "parameters": {
                "type": "object",
                "properties": {
                    "course_id": {
                        "type": "string",
                        "description": "The UUID of the course"
                    }
                },
                "required": ["course_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_user_enrollment_status",
            "description": "Get user's enrollment status and progress for a specific course or all courses",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The UUID of the user"
                    },
                    "course_id": {
                        "type": "string",
                        "description": "Optional: The UUID of a specific course"
                    }
                },
                "required": ["user_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_subscription_status",
            "description": "Get user's subscription status, plan details, and payment information",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The UUID of the user"
                    }
                },
                "required": ["user_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_lesson_content",
            "description": "Get lesson content including transcript, description, and metadata",
            "parameters": {
                "type": "object",
                "properties": {
                    "lesson_id": {
                        "type": "string",
                        "description": "The UUID of the lesson"
                    }
                },
                "required": ["lesson_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_available_courses",
            "description": "List all available courses with optional category and difficulty filters",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Optional: Filter by category (e.g., 'Sanskrit', 'Ayurveda')"
                    },
                    "difficulty": {
                        "type": "string",
                        "description": "Optional: Filter by difficulty level (beginner, intermediate, advanced)",
                        "enum": ["beginner", "intermediate", "advanced"]
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "translate_sanskrit",
            "description": "Translate Sanskrit text to English, Hindi, or other languages",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The Sanskrit text to translate"
                    },
                    "target_language": {
                        "type": "string",
                        "description": "Target language for translation",
                        "enum": ["english", "hindi", "tamil", "kannada"]
                    }
                },
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_payment_plans",
            "description": "Get information about available subscription plans and pricing",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]

def execute_mcp_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Execute an MCP tool by name with given arguments"""
    tools_map = {
        'get_course_info': MCPTools.get_course_info,
        'get_user_enrollment_status': MCPTools.get_user_enrollment_status,
        'get_subscription_status': MCPTools.get_subscription_status,
        'get_lesson_content': MCPTools.get_lesson_content,
        'list_available_courses': MCPTools.list_available_courses,
        'translate_sanskrit': MCPTools.translate_sanskrit,
        'get_payment_plans': MCPTools.get_payment_plans,
    }
    
    tool_func = tools_map.get(tool_name)
    if not tool_func:
        return {'success': False, 'error': f'Unknown tool: {tool_name}'}
    
    try:
        return tool_func(**arguments)
    except Exception as e:
        return {'success': False, 'error': f'Tool execution failed: {str(e)}'}
