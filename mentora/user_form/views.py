from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .models import Academic, Wellbeing

def academic_form_view(request):
    # Fetch all incomplete academic tasks
    tasks = Academic.objects.filter(completed=False)
    return render(request, 'user_form/academic_form.html', {'tasks': tasks})

def wellbeing_form_view(request):
    # Fetch all incomplete wellbeing entries
    entries = Wellbeing.objects.filter(completed=False)
    return render(request, 'user_form/wellbeing_form.html', {'entries': entries})

@csrf_exempt
@require_http_methods(["POST"])
def save_academic_task(request):
    try:
        data = json.loads(request.body)
        task = Academic.objects.create(
            subject=data['subject'],
            grade=data['grade'],
            notes=data.get('notes', '')
        )
        return JsonResponse({
            'success': True,
            'task': {
                'id': task.id,
                'subject': task.subject,
                'grade': task.grade,
                'notes': task.notes,
                'created_at': task.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@require_http_methods(["POST"])
def save_wellbeing_entry(request):
    try:
        data = json.loads(request.body)
        entry = Wellbeing.objects.create(
            mood=data['mood'],
            sleep_hours=int(data['sleep_hours']),
            remarks=data.get('remarks', '')
        )
        return JsonResponse({
            'success': True,
            'entry': {
                'id': entry.id,
                'mood': entry.mood,
                'sleep_hours': entry.sleep_hours,
                'remarks': entry.remarks,
                'created_at': entry.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@require_http_methods(["POST"])
def complete_academic_task(request, task_id):
    try:
        task = Academic.objects.get(id=task_id)
        task.completed = True
        task.save()
        return JsonResponse({'success': True})
    except Academic.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Task not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@require_http_methods(["POST"])
def complete_wellbeing_entry(request, entry_id):
    try:
        entry = Wellbeing.objects.get(id=entry_id)
        entry.completed = True
        entry.save()
        return JsonResponse({'success': True})
    except Wellbeing.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Entry not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@require_http_methods(["DELETE"])
def delete_academic_task(request, task_id):
    try:
        task = Academic.objects.get(id=task_id)
        task.delete()
        return JsonResponse({'success': True})
    except Academic.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Task not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@require_http_methods(["DELETE"])
def delete_wellbeing_entry(request, entry_id):
    try:
        entry = Wellbeing.objects.get(id=entry_id)
        entry.delete()
        return JsonResponse({'success': True})
    except Wellbeing.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Entry not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
