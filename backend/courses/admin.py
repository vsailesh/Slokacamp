from django.contrib import admin
from .models import Course, Lesson, Enrollment, LessonProgress, Review

class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    fields = ('title', 'lesson_type', 'order', 'duration_minutes', 'is_published')

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'difficulty', 'rating', 'total_students', 'is_published', 'created_at')
    list_filter = ('difficulty', 'category', 'is_published', 'created_at')
    search_fields = ('title', 'description', 'instructor_name')
    ordering = ('-created_at',)
    inlines = [LessonInline]
    
    fieldsets = (
        ('Course Info', {'fields': ('title', 'short_description', 'description', 'category', 'difficulty')}),
        ('Instructor', {'fields': ('instructor_name', 'instructor_bio', 'instructor_image')}),
        ('Media', {'fields': ('thumbnail_image',)}),
        ('Stats', {'fields': ('rating', 'total_reviews', 'total_students', 'duration_hours')}),
        ('Publishing', {'fields': ('is_published',)}),
    )

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'lesson_type', 'order', 'duration_minutes', 'is_published')
    list_filter = ('lesson_type', 'is_published', 'course')
    search_fields = ('title', 'description', 'course__title')
    ordering = ('course', 'order')

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'progress_percentage', 'completed_lessons', 'total_lessons', 'enrolled_at')
    list_filter = ('enrolled_at', 'course')
    search_fields = ('user__email', 'course__title')
    ordering = ('-enrolled_at',)
    readonly_fields = ('enrolled_at', 'last_accessed')

@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'lesson', 'is_completed', 'completion_percentage', 'completed_at')
    list_filter = ('is_completed', 'completed_at')
    search_fields = ('user__email', 'lesson__title')
    ordering = ('-updated_at',)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__email', 'course__title', 'comment')
    ordering = ('-created_at',)
