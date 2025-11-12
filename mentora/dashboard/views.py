from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Count, Avg
from datetime import timedelta
from .models import Journal, Habit, Goal, Mood, StudyPlan
from .ai_service import ai_core


def home_view(request):
    """Home page - redirect to dashboard if authenticated"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'home.html')


@login_required
def dashboard_home(request):
    """Main dashboard view with all modules overview"""
    user = request.user
    
    # Get recent data for dashboard
    recent_journals = Journal.objects.filter(user=user).order_by('-created_at')[:3]
    active_habits = Habit.objects.filter(user=user, is_active=True).order_by('-streak')[:5]
    active_goals = Goal.objects.filter(user=user, is_completed=False).order_by('-created_at')[:5]
    recent_moods = Mood.objects.filter(user=user).order_by('-created_at')[:7]
    active_study_plans = StudyPlan.objects.filter(user=user, is_active=True).order_by('-created_at')[:3]
    
    # Calculate statistics
    total_journals = Journal.objects.filter(user=user).count()
    total_habits = Habit.objects.filter(user=user).count()
    total_goals = Goal.objects.filter(user=user).count()
    avg_mood = recent_moods.aggregate(avg=Avg('mood_scale'))['avg'] or 5
    
    # Get AI insights
    mood_data = [{'mood_scale': m.mood_scale, 'date': m.date} for m in recent_moods]
    mood_insight = ai_core.analyze_mood(mood_data)
    
    # Get latest journal reflection
    latest_journal = recent_journals.first()
    latest_reflection = latest_journal.summary if latest_journal else "Start journaling to get AI reflections!"
    
    # Calculate mood bar heights for chart (percentage of max height)
    mood_chart_data = []
    for mood in recent_moods[:7]:
        mood_chart_data.append({
            'mood': mood,
            'height_percent': mood.mood_scale * 10  # Scale 1-10 to 10%-100%
        })
    
    context = {
        'user': user,
        'recent_journals': recent_journals,
        'active_habits': active_habits,
        'active_goals': active_goals,
        'recent_moods': recent_moods,
        'mood_chart_data': mood_chart_data,
        'active_study_plans': active_study_plans,
        'total_journals': total_journals,
        'total_habits': total_habits,
        'total_goals': total_goals,
        'avg_mood': round(avg_mood, 1),
        'mood_insight': mood_insight,
        'latest_reflection': latest_reflection,
    }
    
    return render(request, 'dashboard/index.html', context)


@login_required
def journal_list(request):
    """List all journal entries"""
    journals = Journal.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'dashboard/journal_list.html', {'journals': journals})


@login_required
def journal_create(request):
    """Create a new journal entry"""
    if request.method == 'POST':
        entry_text = request.POST.get('entry_text', '').strip()
        if entry_text:
            journal = Journal.objects.create(
                user=request.user,
                entry_text=entry_text
            )
            # Generate AI reflection
            ai_result = ai_core.summarize_journal(entry_text)
            journal.summary = ai_result['summary']
            journal.mood_tone = ai_result['mood_tone']
            journal.save()
            
            messages.success(request, 'Journal entry saved! AI reflection generated.')
            return redirect('journal_list')
        else:
            messages.error(request, 'Please enter some text for your journal entry.')
    
    return render(request, 'dashboard/journal_form.html')


@login_required
def habit_list(request):
    """List all habits"""
    habits = Habit.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'dashboard/habit_list.html', {'habits': habits})


@login_required
def habit_create(request):
    """Create a new habit"""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        if name:
            Habit.objects.create(
                user=request.user,
                name=name,
                description=description
            )
            messages.success(request, 'Habit created successfully!')
            return redirect('habit_list')
        else:
            messages.error(request, 'Please enter a habit name.')
    
    return render(request, 'dashboard/habit_form.html')


@login_required
def habit_complete(request, habit_id):
    """Mark a habit as completed for today"""
    habit = get_object_or_404(Habit, id=habit_id, user=request.user)
    today = timezone.now().date()
    
    from .models import HabitCompletion
    completion, created = HabitCompletion.objects.get_or_create(
        habit=habit,
        completed_at=today
    )
    
    if created:
        habit.last_completed = today
        habit.update_streak()
        # Update progress
        recent_completions = HabitCompletion.objects.filter(
            habit=habit,
            completed_at__gte=today - timedelta(days=7)
        ).count()
        habit.progress = min(100.0, (recent_completions / 7) * 100)
        habit.save()
        messages.success(request, f'{habit.name} completed! Streak: {habit.streak} days')
    else:
        messages.info(request, f'{habit.name} already completed today')
    
    return redirect('habit_list')


@login_required
def goal_list(request):
    """List all goals"""
    goals = Goal.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'dashboard/goal_list.html', {'goals': goals})


@login_required
def goal_create(request):
    """Create a new goal"""
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        goal_type = request.POST.get('goal_type', 'short')
        target_date = request.POST.get('target_date') or None
        
        if title:
            Goal.objects.create(
                user=request.user,
                title=title,
                description=description,
                goal_type=goal_type,
                target_date=target_date
            )
            messages.success(request, 'Goal created successfully!')
            return redirect('goal_list')
        else:
            messages.error(request, 'Please enter a goal title.')
    
    return render(request, 'dashboard/goal_form.html')


@login_required
def mood_track(request):
    """Track mood"""
    if request.method == 'POST':
        mood_emoji = request.POST.get('mood_emoji', '😐')
        mood_scale = int(request.POST.get('mood_scale', 5))
        notes = request.POST.get('notes', '').strip()
        today = timezone.now().date()
        
        mood, created = Mood.objects.update_or_create(
            user=request.user,
            date=today,
            defaults={
                'mood_emoji': mood_emoji,
                'mood_scale': mood_scale,
                'notes': notes
            }
        )
        
        if created:
            messages.success(request, 'Mood logged successfully!')
        else:
            messages.info(request, 'Mood updated for today!')
        
        return redirect('mood_analytics')
    
    # Get today's mood if exists
    today = timezone.now().date()
    today_mood = Mood.objects.filter(user=request.user, date=today).first()
    
    # Get mood choices from model
    mood_choices = Mood.MOOD_CHOICES
    
    return render(request, 'dashboard/mood_form.html', {
        'today_mood': today_mood,
        'mood_choices': mood_choices
    })


@login_required
def mood_analytics(request):
    """Mood analytics and insights"""
    moods = Mood.objects.filter(user=request.user).order_by('-created_at')[:14]
    mood_data = [{'mood_scale': m.mood_scale, 'date': m.date} for m in moods]
    insight = ai_core.analyze_mood(mood_data)
    
    # Calculate mood bar heights for chart (pixels, max 180px for h-48 container)
    mood_chart_data = []
    for mood in moods:
        mood_chart_data.append({
            'mood': mood,
            'height_px': int(mood.mood_scale * 18)  # Scale 1-10 to 18-180px
        })
    
    context = {
        'moods': moods,
        'mood_chart_data': mood_chart_data,
        'insight': insight,
        'avg_mood': round(sum(m.mood_scale for m in moods) / len(moods), 1) if moods else 0
    }
    
    return render(request, 'dashboard/mood_analytics.html', context)


@login_required
def study_plan_list(request):
    """List all study plans"""
    study_plans = StudyPlan.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'dashboard/study_plan_list.html', {'study_plans': study_plans})


@login_required
def study_plan_create(request):
    """Create a new study plan"""
    if request.method == 'POST':
        subject = request.POST.get('subject', '').strip()
        description = request.POST.get('description', '').strip()
        
        if subject:
            # Generate AI study plan
            subjects = [subject]
            goals = [description] if description else []
            ai_plan = ai_core.generate_study_plan(subjects, goals)
            
            StudyPlan.objects.create(
                user=request.user,
                subject=subject,
                description=ai_plan['description'],
                schedule=ai_plan['schedule']
            )
            messages.success(request, 'Study plan created with AI assistance!')
            return redirect('study_plan_list')
        else:
            messages.error(request, 'Please enter a subject.')
    
    return render(request, 'dashboard/study_plan_form.html')
