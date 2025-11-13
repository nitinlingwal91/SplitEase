from django.contrib import admin
from .models import Activity

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ['user', 'group', 'activity_type', 'timestamp']
    list_filter = ['activity_type', 'timestamp', 'group']
    search_fields = ['user__name', 'group__name', 'description']
    readonly_fields = ['timestamp']
