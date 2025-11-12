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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Habit'
        verbose_name_plural = 'Habits'

    def __str__(self):
        return f"{self.user.username} - {self.name}"

    def update_streak(self):
        """Update streak based on last completion date"""
        if self.last_completed:
            days_since = (timezone.now().date() - self.last_completed).days
            if days_since == 0:
                # Completed today, increment streak
                self.streak += 1
            elif days_since == 1:
                # Completed yesterday, maintain streak
                pass
            else:
                # Streak broken
                self.streak = 1
        else:
            self.streak = 0


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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Study Plan'
        verbose_name_plural = 'Study Plans'

    def __str__(self):
        return f"{self.user.username} - {self.subject}"


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
