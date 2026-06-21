from django.contrib import admin
from .models import Feedback


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'subject', 'short_message', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('subject', 'message', 'user__username')
    readonly_fields = ('user', 'subject', 'message', 'created_at')

    def short_message(self, obj):
        return (obj.message[:60] + '…') if len(obj.message) > 60 else obj.message
    short_message.short_description = 'Message'

    def has_add_permission(self, request):
        # Feedback is created by users through the form, not in the admin.
        return False
