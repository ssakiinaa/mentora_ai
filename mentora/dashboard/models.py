from datetime import timedelta

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Journal(models.Model):
    """Daily journal entries with AI-generated reflections"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='journals')
    entry_text = models.TextField()
    summary = models.TextField(blank=True)
    mood_tone = models.CharField(max_length=50, blank=True)  # e.g., "positive", "reflective", "anxious"
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Journal Entry'
        verbose_name_plural = 'Journal Entries'

    def __str__(self):
        return f"{self.user.username} - {self.created_at.strftime('%Y-%m-%d')}"


class Habit(models.Model):
    """Daily habits with streak tracking and progress"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='habits')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    progress = models.FloatField(default=0.0)  # 0.0 to 100.0
    streak = models.IntegerField(default=0)
    last_completed = models.DateField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    target_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Habit'
        verbose_name_plural = 'Habits'

    def __str__(self):
        return f"{self.user.username} - {self.name}"

    def record_completion(self, completion_date=None):
        """Record a habit completion and adjust streak based on the previous completion date."""
        completion_date = completion_date or timezone.now().date()
        if self.last_completed == completion_date:
            return False

        if self.last_completed:
            days_since = (completion_date - self.last_completed).days
            if days_since == 1:
                self.streak = max(1, self.streak + 1)
            else:
                self.streak = 1
        else:
            self.streak = 1

        self.last_completed = completion_date
        return True

    def get_expected_days(self, until=None):
        until = until or timezone.now().date()
        start = self.start_date or (self.created_at.date() if self.created_at else until)
        end = min(until, self.target_date) if self.target_date else until
        delta = (end - start).days + 1
        return max(1, delta)

    def recalc_progress(self):
        """Recalculate habit progress from daily completions and timeframe."""
        if self.start_date or self.target_date:
            expected = self.get_expected_days()
            completed = self.completions.filter(completed_at__lte=timezone.now().date()).count()
            self.progress = min(100.0, (completed / expected) * 100)
        else:
            recent_completions = self.completions.filter(
                completed_at__gte=timezone.now().date() - timedelta(days=6)
            ).count()
            self.progress = min(100.0, (recent_completions / 7) * 100)
        self.save()


class HabitCompletion(models.Model):
    """Track daily habit completions"""
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name='completions')
    completed_at = models.DateField(default=timezone.now)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ['habit', 'completed_at']
        ordering = ['-completed_at']
        verbose_name = 'Habit Completion'
        verbose_name_plural = 'Habit Completions'

    def __str__(self):
        return f"{self.habit.name} - {self.completed_at}"


class Goal(models.Model):
    """Short-term and long-term goals"""
    GOAL_TYPE_CHOICES = [
        ('short', 'Short-term'),
        ('long', 'Long-term'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='goals')
    goal_type = models.CharField(max_length=20, choices=GOAL_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    progress = models.FloatField(default=0.0)  # 0.0 to 100.0
    start_date = models.DateField(null=True, blank=True)
    target_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_completed = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Goal'
        verbose_name_plural = 'Goals'

    def __str__(self):
        return f"{self.user.username} - {self.title}"

    def total_timeframe_days(self):
        if self.target_date:
            start = self.start_date or self.created_at.date()
            if self.target_date >= start:
                return max(1, (self.target_date - start).days + 1)
        return 0

    def recalc_progress(self):
        if self.total_timeframe_days() > 0:
            completed = self.completions.count()
            self.progress = min(100.0, (completed / self.total_timeframe_days()) * 100)
        if self.target_date and timezone.now().date() >= self.target_date and self.progress >= 100:
            self.is_completed = True
        self.save()


class GoalCompletion(models.Model):
    """Track daily goal check-ins"""
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name='completions')
    completed_at = models.DateField(default=timezone.now)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ['goal', 'completed_at']
        ordering = ['-completed_at']
        verbose_name = 'Goal Completion'
        verbose_name_plural = 'Goal Completions'

    def __str__(self):
        return f"{self.goal.title} - {self.completed_at}"


class Mood(models.Model):
    """Daily mood tracking with emoji/scale"""
    MOOD_CHOICES = [
        ('😊', 'Happy'),
        ('😌', 'Calm'),
        ('😐', 'Neutral'),
        ('😟', 'Worried'),
        ('😢', 'Sad'),
        ('😡', 'Angry'),
        ('😴', 'Tired'),
        ('🤔', 'Reflective'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='moods')
    mood_emoji = models.CharField(max_length=10, choices=MOOD_CHOICES, default='😐')
    mood_scale = models.IntegerField(default=5)  # 1-10 scale
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    date = models.DateField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'date']
        verbose_name = 'Mood Entry'
        verbose_name_plural = 'Mood Entries'

    def __str__(self):
        return f"{self.user.username} - {self.mood_emoji} ({self.date})"


class StudyPlan(models.Model):
    """AI-generated personalized study plans"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='study_plans')
    subject = models.CharField(max_length=100)
    description = models.TextField()
    schedule = models.JSONField(default=dict)  # Store daily schedule as JSON
    progress = models.FloatField(default=0.0)  # 0.0 to 100.0
    start_date = models.DateField(null=True, blank=True)
    target_date = models.DateField(null=True, blank=True)
    target_minutes = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Study Plan'
        verbose_name_plural = 'Study Plans'

    def __str__(self):
        return f"{self.user.username} - {self.subject}"

    @property
    def target_hours(self):
        return self.target_minutes / 60 if self.target_minutes else 0

    def recalc_progress(self):
        total_minutes = sum(session.duration_minutes for session in self.sessions.all())
        if self.target_minutes > 0:
            self.progress = min(100.0, (total_minutes / self.target_minutes) * 100)
        elif self.start_date and self.target_date and self.start_date <= self.target_date:
            planned_days = (self.target_date - self.start_date).days + 1
            completed_days = len({session.completed_at.date() for session in self.sessions.all() if session.completed_at.date() <= timezone.now().date()})
            self.progress = min(100.0, (completed_days / planned_days) * 100)
        else:
            self.progress = min(100.0, (total_minutes / (20 * 60)) * 100)
        self.save()


class StudySession(models.Model):
    """Track individual study sessions"""
    study_plan = models.ForeignKey(StudyPlan, on_delete=models.CASCADE, related_name='sessions')
    duration_minutes = models.IntegerField(default=0)
    topics_covered = models.TextField(blank=True)
    completed_at = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-completed_at']
        verbose_name = 'Study Session'
        verbose_name_plural = 'Study Sessions'

    def __str__(self):
        return f"{self.study_plan.subject} - {self.completed_at.strftime('%Y-%m-%d %H:%M')}"
