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
    path('habits/<int:habit_id>/extend-deadline/', views.habit_extend_deadline, name='habit_extend_deadline'),
    path('habits/<int:habit_id>/update/', views.habit_update, name='habit_update'),
    # Goal routes
    path('goals/', views.goal_list, name='goal_list'),
    path('goals/create/', views.goal_create, name='goal_create'),
    path('goals/<int:goal_id>/extend-deadline/', views.goal_extend_deadline, name='goal_extend_deadline'),
    path('goals/<int:goal_id>/update/', views.goal_update, name='goal_update'),
    path('goals/<int:goal_id>/complete/', views.goal_complete, name='goal_complete'),
    # AI Coach chat routes
    path('chat/', views.ai_chat, name='ai_chat'),
    path('chat/reply/', views.ai_chat_reply, name='ai_chat_reply'),
    # Mood routes
    path('mood/', views.mood_track, name='mood_track'),
    path('mood/analytics/', views.mood_analytics, name='mood_analytics'),
    # Study plan routes
    path('study-plans/', views.study_plan_list, name='study_plan_list'),
    path('study-plans/create/', views.study_plan_create, name='study_plan_create'),
    path('study-plans/<int:plan_id>/edit/', views.study_plan_edit, name='study_plan_edit'),
    path('study-plans/<int:plan_id>/checkin/', views.study_plan_checkin, name='study_plan_checkin'),
    path('study-plans/<int:plan_id>/delete/', views.study_plan_delete, name='study_plan_delete'),
]
