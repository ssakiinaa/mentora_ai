from django import forms
from .models import Feedback

INPUT_CLASS = (
    'w-full px-3 py-2 rounded-lg bg-[var(--bg-secondary)] '
    'border border-[var(--border-color)] text-[var(--text-primary)] '
    'focus:outline-none focus:ring-2 focus:ring-[var(--accent-primary)]'
)


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['subject', 'message']
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': INPUT_CLASS,
                'placeholder': 'Subject (optional)',
            }),
            'message': forms.Textarea(attrs={
                'class': INPUT_CLASS,
                'rows': 5,
                'placeholder': 'Tell us what you think...',
            }),
        }
