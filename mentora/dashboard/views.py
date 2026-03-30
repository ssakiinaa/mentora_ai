from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Count, Avg
from datetime import date, timedelta
from .models import Journal, Habit, Goal, Mood, StudyPlan, GoalCompletion, StudySession
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
def ai_chat(request):
    """Render the AI coaching chat page"""
    user = request.user
    recent_journals = Journal.objects.filter(user=user).order_by('-created_at')[:3]
    active_habits = Habit.objects.filter(user=user, is_active=True).order_by('-created_at')[:4]
    active_goals = Goal.objects.filter(user=user, is_completed=False).order_by('-created_at')[:4]
    recent_moods = Mood.objects.filter(user=user).order_by('-created_at')[:7]

    journal_snippets = [journal.entry_text[:120] for journal in recent_journals]
    habit_snippets = [f"{habit.name}: {habit.progress:.0f}% progress, streak {habit.streak}" for habit in active_habits]
    goal_snippets = [f"{goal.title}: {goal.progress:.0f}%" for goal in active_goals]
    mood_snippets = [f"{mood.mood_emoji} {mood.mood_scale}/10" for mood in recent_moods]

    context = {
        'recent_journals': recent_journals,
        'active_habits': active_habits,
        'active_goals': active_goals,
        'recent_moods': recent_moods,
        'journal_snippets': journal_snippets,
        'habit_snippets': habit_snippets,
        'goal_snippets': goal_snippets,
        'mood_snippets': mood_snippets,
    }
    return render(request, 'dashboard/chat.html', context)


@login_required
def ai_chat_reply(request):
    """Return a coaching reply for the chat interface."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method.'}, status=405)

    user_question = request.POST.get('message', '').strip()
    if not user_question:
        return JsonResponse({'error': 'Please ask a question to continue the chat.'}, status=400)

    user = request.user
    recent_journals = Journal.objects.filter(user=user).order_by('-created_at')[:5]
    active_habits = Habit.objects.filter(user=user, is_active=True).order_by('-created_at')[:5]
    active_goals = Goal.objects.filter(user=user, is_completed=False).order_by('-created_at')[:5]
    recent_moods = Mood.objects.filter(user=user).order_by('-created_at')[:7]

    context_lines = []
    if active_goals:
        context_lines.append('Recent active goals:')
        for goal in active_goals:
            context_lines.append(f'- {goal.title} ({goal.progress:.0f}% complete)')

    if active_habits:
        context_lines.append('Recent habits:')
        for habit in active_habits:
            context_lines.append(f'- {habit.name}: {habit.progress:.0f}% progress, streak {habit.streak}')

    if recent_journals:
        context_lines.append('Recent journal themes:')
        for journal in recent_journals:
            context_lines.append(f'- {journal.created_at.date()}: {journal.entry_text[:120]}')

    if recent_moods:
        context_lines.append('Mood history:')
        for mood in recent_moods:
            context_lines.append(f'- {mood.date}: {mood.mood_emoji} {mood.mood_scale}/10')

    user_context = '\n'.join(context_lines)
    ai_reply = ai_core.generate_coaching_response(user_question, user_context)

    return JsonResponse({'reply': ai_reply})


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
        start_date_value = request.POST.get('start_date', '').strip()
        target_date_value = request.POST.get('target_date', '').strip()
        start_date = date.fromisoformat(start_date_value) if start_date_value else None
        target_date = date.fromisoformat(target_date_value) if target_date_value else None

        if name:
            Habit.objects.create(
                user=request.user,
                name=name,
                description=description,
                start_date=start_date,
                target_date=target_date
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
        habit.recalc_progress()
        messages.success(request, f'{habit.name} completed! Streak: {habit.streak} days')
    else:
        messages.info(request, f'{habit.name} already completed today')
    
    return redirect('habit_list')


@login_required
def habit_extend_deadline(request, habit_id):
    """Extend the habit deadline by a selectable number of days."""
    habit = get_object_or_404(Habit, id=habit_id, user=request.user)
    if request.method == 'POST':
        days_value = request.POST.get('days', '').strip()
        try:
            days = int(days_value)
            if days not in (5, 10, 15):
                raise ValueError
        except ValueError:
            messages.error(request, 'Invalid extension period.')
            return redirect('habit_list')

        base_date = habit.target_date or habit.start_date or timezone.now().date()
        habit.target_date = base_date + timedelta(days=days)
        habit.save()
        messages.success(request, f'Habit deadline extended by {days} days.')
    return redirect('habit_list')


@login_required
def habit_update(request, habit_id):
    """Update habit progress directly from the habit list."""
    habit = get_object_or_404(Habit, id=habit_id, user=request.user)
    if request.method == 'POST':
        progress_value = request.POST.get('progress', '').strip()
        try:
            progress = float(progress_value)
            habit.progress = max(0.0, min(100.0, progress))
            habit.save()
            messages.success(request, f'Habit progress updated to {habit.progress:.0f}%')
        except ValueError:
            messages.error(request, 'Please enter a valid progress percentage between 0 and 100.')
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
        start_date_value = request.POST.get('start_date', '').strip()
        target_date_value = request.POST.get('target_date', '').strip()
        start_date = date.fromisoformat(start_date_value) if start_date_value else None
        target_date = date.fromisoformat(target_date_value) if target_date_value else None
        
        if title:
            Goal.objects.create(
                user=request.user,
                title=title,
                description=description,
                goal_type=goal_type,
                start_date=start_date,
                target_date=target_date
            )
            messages.success(request, 'Goal created successfully!')
            return redirect('goal_list')
        else:
            messages.error(request, 'Please enter a goal title.')
    
    return render(request, 'dashboard/goal_form.html')


@login_required
def goal_update(request, goal_id):
    """Update goal progress from the goal list."""
    goal = get_object_or_404(Goal, id=goal_id, user=request.user)
    if request.method == 'POST':
        progress_value = request.POST.get('progress', '').strip()
        try:
            progress = float(progress_value)
            goal.progress = max(0.0, min(100.0, progress))
            if goal.progress >= 100:
                goal.progress = 100.0
                goal.is_completed = True
            goal.save()
            messages.success(request, f'Goal progress updated to {goal.progress:.0f}%')
        except ValueError:
            messages.error(request, 'Please enter a valid goal progress percentage between 0 and 100.')
    return redirect('goal_list')


@login_required
def goal_complete(request, goal_id):
    """Mark goal as checked in for today"""
    goal = get_object_or_404(Goal, id=goal_id, user=request.user)
    today = timezone.now().date()
    completion, created = GoalCompletion.objects.get_or_create(
        goal=goal,
        completed_at=today
    )
    if created:
        goal.recalc_progress()
        messages.success(request, f'{goal.title} checked in for today!')
    else:
        messages.info(request, f'{goal.title} already checked in today.')
    return redirect('goal_list')


@login_required
def goal_extend_deadline(request, goal_id):
    """Extend the goal deadline by a selectable number of days."""
    goal = get_object_or_404(Goal, id=goal_id, user=request.user)
    if request.method == 'POST':
        days_value = request.POST.get('days', '').strip()
        try:
            days = int(days_value)
            if days not in (5, 10, 15):
                raise ValueError
        except ValueError:
            messages.error(request, 'Invalid extension period.')
            return redirect('goal_list')

        base_date = goal.target_date or goal.start_date or timezone.now().date()
        goal.target_date = base_date + timedelta(days=days)
        goal.save()
        messages.success(request, f'Goal deadline extended by {days} days.')
    return redirect('goal_list')


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
        start_date_value = request.POST.get('start_date', '').strip()
        target_date_value = request.POST.get('target_date', '').strip()
        target_hours_value = request.POST.get('target_hours', '').strip()
        start_date = date.fromisoformat(start_date_value) if start_date_value else None
        target_date = date.fromisoformat(target_date_value) if target_date_value else None
        try:
            target_hours = float(target_hours_value) if target_hours_value else 0
        except ValueError:
            target_hours = 0
        target_minutes = int(target_hours * 60)
        
        if subject:
            # Generate AI study plan
            subjects = [subject]
            goals = [description] if description else []
            ai_plan = ai_core.generate_study_plan(subjects, goals)
            
            StudyPlan.objects.create(
                user=request.user,
                subject=subject,
                description=ai_plan['description'],
                schedule=ai_plan['schedule'],
                start_date=start_date,
                target_date=target_date,
                target_minutes=target_minutes
            )
            messages.success(request, 'Study plan created with AI assistance!')
            return redirect('study_plan_list')
        else:
            messages.error(request, 'Please enter a subject.')
    
    return render(request, 'dashboard/study_plan_form.html')


@login_required
def study_plan_edit(request, plan_id):
    """Edit an existing study plan."""
    plan = get_object_or_404(StudyPlan, id=plan_id, user=request.user)
    if request.method == 'POST':
        subject = request.POST.get('subject', '').strip()
        description = request.POST.get('description', '').strip()
        progress_value = request.POST.get('progress', '').strip()
        is_active_value = request.POST.get('is_active', 'on')
        start_date_value = request.POST.get('start_date', '').strip()
        target_date_value = request.POST.get('target_date', '').strip()
        target_hours_value = request.POST.get('target_hours', '').strip()
        start_date = date.fromisoformat(start_date_value) if start_date_value else None
        target_date = date.fromisoformat(target_date_value) if target_date_value else None
        try:
            target_hours = float(target_hours_value) if target_hours_value else 0
        except ValueError:
            target_hours = 0
        target_minutes = int(target_hours * 60)

        if subject:
            plan.subject = subject
            plan.description = description or plan.description
            plan.start_date = start_date
            plan.target_date = target_date
            plan.target_minutes = target_minutes
            if progress_value:
                try:
                    plan.progress = max(0.0, min(100.0, float(progress_value)))
                except ValueError:
                    messages.error(request, 'Please enter a valid progress percentage between 0 and 100.')
                    return render(request, 'dashboard/study_plan_form.html', {'plan': plan, 'edit_mode': True})

            plan.is_active = (is_active_value == 'on')
            plan.save()
            plan.recalc_progress()
            messages.success(request, 'Study plan updated successfully!')
            return redirect('study_plan_list')
        else:
            messages.error(request, 'Please enter a subject.')

    return render(request, 'dashboard/study_plan_form.html', {'plan': plan, 'edit_mode': True})


@login_required
def study_plan_checkin(request, plan_id):
    """Log a daily study session for the plan."""
    plan = get_object_or_404(StudyPlan, id=plan_id, user=request.user)
    if request.method == 'POST':
        duration_value = request.POST.get('duration_minutes', '30').strip()
        try:
            duration_minutes = max(0, int(duration_value))
        except ValueError:
            duration_minutes = 30

        if not plan.start_date:
            plan.start_date = timezone.now().date()
            plan.save()

        StudySession.objects.create(
            study_plan=plan,
            duration_minutes=duration_minutes,
            topics_covered=request.POST.get('topics_covered', 'Daily check-in'),
            notes=request.POST.get('notes', 'Completed today')
        )
        plan.recalc_progress()
        messages.success(request, 'Study plan checked in for today!')
    return redirect('study_plan_list')


@login_required
def study_plan_delete(request, plan_id):
    """Delete a study plan."""
    plan = get_object_or_404(StudyPlan, id=plan_id, user=request.user)
    if request.method == 'POST':
        plan.delete()
        messages.success(request, 'Study plan deleted successfully.')
    return redirect('study_plan_list')
