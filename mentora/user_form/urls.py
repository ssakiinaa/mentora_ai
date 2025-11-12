from django.urls import path
from . import views

urlpatterns = [
    path('academic/', views.academic_form_view, name='academic_form'),
    path('wellbeing/', views.wellbeing_form_view, name='wellbeing_form'),
    path('api/academic/save/', views.save_academic_task, name='save_academic_task'),
    path('api/wellbeing/save/', views.save_wellbeing_entry, name='save_wellbeing_entry'),
    path('api/academic/<int:task_id>/complete/', views.complete_academic_task, name='complete_academic_task'),
    path('api/wellbeing/<int:entry_id>/complete/', views.complete_wellbeing_entry, name='complete_wellbeing_entry'),
    path('api/academic/<int:task_id>/delete/', views.delete_academic_task, name='delete_academic_task'),
    path('api/wellbeing/<int:entry_id>/delete/', views.delete_wellbeing_entry, name='delete_wellbeing_entry'),
]
