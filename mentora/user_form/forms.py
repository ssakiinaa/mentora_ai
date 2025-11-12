from django import forms
from .models import Academic, Wellbeing

class AcademicForm(forms.ModelForm):
    class Meta:
        model = Academic
        fields = ['subject', 'grade', 'notes']

class WellbeingForm(forms.ModelForm):
    class Meta:
        model = Wellbeing
        fields = ['mood', 'sleep_hours', 'remarks']
