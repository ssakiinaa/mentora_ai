from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.db.models import Max


def login_view(request):
    return render(request, 'users/login.html')

def logout_view(request):
    logout(request)
    response = redirect('home')

    # Optional: Clear Google session by redirecting to Google's logout URL
    response.delete_cookie('sessionid')  # Optional cleanup
    return response

    # return render(request ,"home.html")

@login_required
def profile_view(request):
    from dashboard.models import Journal, Habit, Goal, Mood, StudyPlan
    from django.db.models import Count, Avg
    from datetime import timedelta
    from django.utils import timezone
    
    user = request.user
    
    # Calculate AI engagement statistics
    total_journals = Journal.objects.filter(user=user).count()
    total_habits = Habit.objects.filter(user=user).count()
    total_goals = Goal.objects.filter(user=user).count()
    total_moods = Mood.objects.filter(user=user).count()
    total_study_plans = StudyPlan.objects.filter(user=user).count()
    
    # Recent activity (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_journals = Journal.objects.filter(user=user, created_at__gte=thirty_days_ago).count()
    recent_moods = Mood.objects.filter(user=user, created_at__gte=thirty_days_ago).count()
    
    # Calculate engagement score
    engagement_score = (total_journals * 2) + (total_habits * 3) + (total_goals * 2) + (total_moods * 1) + (total_study_plans * 3)
    
    # Get average mood
    avg_mood = Mood.objects.filter(user=user).aggregate(avg=Avg('mood_scale'))['avg'] or 0
    
    # Get longest habit streak
    longest_streak = Habit.objects.filter(user=user).aggregate(max_streak=Max('streak'))['max_streak'] or 0
    
    context = {
        'user': user,
        'total_journals': total_journals,
        'total_habits': total_habits,
        'total_goals': total_goals,
        'total_moods': total_moods,
        'total_study_plans': total_study_plans,
        'recent_journals': recent_journals,
        'recent_moods': recent_moods,
        'engagement_score': engagement_score,
        'avg_mood': round(avg_mood, 1) if avg_mood else 0,
        'longest_streak': longest_streak,
    }
    
    return render(request, 'users/profile.html', context)

