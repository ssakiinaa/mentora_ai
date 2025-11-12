from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_home, name='dashboard'),
    # Journal routes
    path('journals/', views.journal_list, name='journal_list'),
    path('journals/create/', views.journal_create, name='journal_create'),
    # Habit routes
    path('habits/', views.habit_list, name='habit_list'),
    path('habits/create/', views.habit_create, name='habit_create'),
    path('habits/<int:habit_id>/complete/', views.habit_complete, name='habit_complete'),
    # Goal routes
    path('goals/', views.goal_list, name='goal_list'),
    path('goals/create/', views.goal_create, name='goal_create'),
    # Mood routes
    path('mood/', views.mood_track, name='mood_track'),
    path('mood/analytics/', views.mood_analytics, name='mood_analytics'),
    # Study plan routes
    path('study-plans/', views.study_plan_list, name='study_plan_list'),
    path('study-plans/create/', views.study_plan_create, name='study_plan_create'),
]
