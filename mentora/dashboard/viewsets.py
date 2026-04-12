"""
DRF ViewSets for Mentora AI API
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q
from .models import Journal, Habit, HabitCompletion, Goal, Mood, StudyPlan, StudySession
from .serializers import (
    JournalSerializer, HabitSerializer, HabitCompletionSerializer,
    GoalSerializer, MoodSerializer, StudyPlanSerializer, StudySessionSerializer,
    AIReflectionSerializer
)
from .ai_service import ai_core


class JournalViewSet(viewsets.ModelViewSet):
    """ViewSet for journal entries"""
    serializer_class = JournalSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Journal.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        journal = serializer.save(user=self.request.user)
        # Generate AI reflection
        ai_result = ai_core.summarize_journal(journal.entry_text)
        journal.summary = ai_result['summary']
        journal.mood_tone = ai_result['mood_tone']
        journal.save()
    
    @action(detail=False, methods=['post'])
    def generate_reflection(self, request):
        """Generate AI reflection for journal entry text"""
        serializer = AIReflectionSerializer(data=request.data)
        if serializer.is_valid():
            entry_text = serializer.validated_data['entry_text']
            ai_result = ai_core.summarize_journal(entry_text)
            return Response(ai_result, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HabitViewSet(viewsets.ModelViewSet):
    """ViewSet for habits"""
    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark habit as completed for today"""
        habit = self.get_object()
        today = timezone.now().date()
        
        # Check if already completed today
        completion, created = HabitCompletion.objects.get_or_create(
            habit=habit,
            completed_at=today,
            defaults={'notes': request.data.get('notes', '')}
        )
        
        if created:
            if habit.record_completion(today):
                habit.recalc_progress()
                habit.save()
            return Response({
                'message': 'Habit completed!',
                'streak': habit.streak,
                'progress': habit.progress
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'message': 'Habit already completed today'
            }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'])
    def nudge(self, request, pk=None):
        """Get AI motivational nudge for habit"""
        habit = self.get_object()
        nudge = ai_core.get_habit_nudge(habit.name, habit.streak, habit.progress)
        return Response({'nudge': nudge})


class GoalViewSet(viewsets.ModelViewSet):
    """ViewSet for goals"""
    serializer_class = GoalSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Goal.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Get goals filtered by type"""
        goal_type = request.query_params.get('type', None)
        queryset = self.get_queryset()
        if goal_type:
            queryset = queryset.filter(goal_type=goal_type)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class MoodViewSet(viewsets.ModelViewSet):
    """ViewSet for mood entries"""
    serializer_class = MoodSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Mood.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Get mood analytics and AI insights"""
        moods = self.get_queryset().order_by('-created_at')[:7]
        mood_data = [{'mood_scale': m.mood_scale, 'date': m.date} for m in moods]
        insight = ai_core.analyze_mood(mood_data)
        
        return Response({
            'insight': insight,
            'recent_moods': MoodSerializer(moods, many=True).data,
            'average_mood': sum(m.mood_scale for m in moods) / len(moods) if moods else 0
        })


class StudyPlanViewSet(viewsets.ModelViewSet):
    """ViewSet for study plans"""
    serializer_class = StudyPlanSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return StudyPlan.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_session(self, request, pk=None):
        """Add a study session to a plan"""
        study_plan = self.get_object()
        session = StudySession.objects.create(
            study_plan=study_plan,
            duration_minutes=request.data.get('duration_minutes', 0),
            topics_covered=request.data.get('topics_covered', ''),
            notes=request.data.get('notes', '')
        )
        # Update plan progress (simplified calculation)
        total_minutes = sum(s.duration_minutes for s in study_plan.sessions.all())
        # Assuming 20 hours per week target
        study_plan.progress = min(100.0, (total_minutes / (20 * 60)) * 100)
        study_plan.save()
        
        return Response(StudySessionSerializer(session).data, status=status.HTTP_201_CREATED)

