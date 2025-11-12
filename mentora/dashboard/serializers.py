"""
DRF Serializers for Mentora AI API
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Journal, Habit, HabitCompletion, Goal, Mood, StudyPlan, StudySession


class UserSerializer(serializers.ModelSerializer):
    """User serializer for profile data"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class JournalSerializer(serializers.ModelSerializer):
    """Serializer for journal entries"""
    user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Journal
        fields = ['id', 'user', 'entry_text', 'summary', 'mood_tone', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'summary', 'mood_tone', 'created_at', 'updated_at']


class HabitCompletionSerializer(serializers.ModelSerializer):
    """Serializer for habit completions"""
    class Meta:
        model = HabitCompletion
        fields = ['id', 'habit', 'completed_at', 'notes']
        read_only_fields = ['id']


class HabitSerializer(serializers.ModelSerializer):
    """Serializer for habits"""
    user = serializers.StringRelatedField(read_only=True)
    completions = HabitCompletionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Habit
        fields = ['id', 'user', 'name', 'description', 'progress', 'streak', 
                  'last_completed', 'created_at', 'updated_at', 'is_active', 'completions']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class GoalSerializer(serializers.ModelSerializer):
    """Serializer for goals"""
    user = serializers.StringRelatedField(read_only=True)
    goal_type_display = serializers.CharField(source='get_goal_type_display', read_only=True)
    
    class Meta:
        model = Goal
        fields = ['id', 'user', 'goal_type', 'goal_type_display', 'title', 'description', 
                  'progress', 'target_date', 'created_at', 'updated_at', 'is_completed']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class MoodSerializer(serializers.ModelSerializer):
    """Serializer for mood entries"""
    user = serializers.StringRelatedField(read_only=True)
    mood_display = serializers.CharField(source='get_mood_emoji_display', read_only=True)
    
    class Meta:
        model = Mood
        fields = ['id', 'user', 'mood_emoji', 'mood_display', 'mood_scale', 'notes', 
                  'created_at', 'date']
        read_only_fields = ['id', 'user', 'created_at']


class StudySessionSerializer(serializers.ModelSerializer):
    """Serializer for study sessions"""
    class Meta:
        model = StudySession
        fields = ['id', 'study_plan', 'duration_minutes', 'topics_covered', 
                  'completed_at', 'notes']
        read_only_fields = ['id']


class StudyPlanSerializer(serializers.ModelSerializer):
    """Serializer for study plans"""
    user = serializers.StringRelatedField(read_only=True)
    sessions = StudySessionSerializer(many=True, read_only=True)
    
    class Meta:
        model = StudyPlan
        fields = ['id', 'user', 'subject', 'description', 'schedule', 'progress', 
                  'created_at', 'updated_at', 'is_active', 'sessions']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class AIReflectionSerializer(serializers.Serializer):
    """Serializer for AI reflection requests"""
    entry_text = serializers.CharField(required=True, max_length=5000)
    
    def validate_entry_text(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Journal entry must be at least 10 characters long.")
        return value

