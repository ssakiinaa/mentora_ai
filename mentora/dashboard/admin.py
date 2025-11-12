from django.contrib import admin
from .models import Journal, Habit, HabitCompletion, Goal, Mood, StudyPlan, StudySession


@admin.register(Journal)
class JournalAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'mood_tone', 'entry_preview']
    list_filter = ['created_at', 'mood_tone']
    search_fields = ['user__username', 'entry_text', 'summary']
    readonly_fields = ['created_at', 'updated_at']
    
    def entry_preview(self, obj):
        return obj.entry_text[:50] + '...' if len(obj.entry_text) > 50 else obj.entry_text
    entry_preview.short_description = 'Entry Preview'


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'streak', 'progress', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['user__username', 'name', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(HabitCompletion)
class HabitCompletionAdmin(admin.ModelAdmin):
    list_display = ['habit', 'completed_at', 'notes_preview']
    list_filter = ['completed_at']
    search_fields = ['habit__name', 'notes']
    
    def notes_preview(self, obj):
        return obj.notes[:30] + '...' if len(obj.notes) > 30 else obj.notes
    notes_preview.short_description = 'Notes'


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'goal_type', 'progress', 'is_completed', 'target_date']
    list_filter = ['goal_type', 'is_completed', 'created_at']
    search_fields = ['user__username', 'title', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Mood)
class MoodAdmin(admin.ModelAdmin):
    list_display = ['user', 'mood_emoji', 'mood_scale', 'date', 'created_at']
    list_filter = ['date', 'mood_emoji', 'created_at']
    search_fields = ['user__username', 'notes']
    readonly_fields = ['created_at']


@admin.register(StudyPlan)
class StudyPlanAdmin(admin.ModelAdmin):
    list_display = ['user', 'subject', 'progress', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['user__username', 'subject', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(StudySession)
class StudySessionAdmin(admin.ModelAdmin):
    list_display = ['study_plan', 'duration_minutes', 'completed_at', 'topics_preview']
    list_filter = ['completed_at']
    search_fields = ['study_plan__subject', 'topics_covered', 'notes']
    
    def topics_preview(self, obj):
        return obj.topics_covered[:30] + '...' if len(obj.topics_covered) > 30 else obj.topics_covered
    topics_preview.short_description = 'Topics'
