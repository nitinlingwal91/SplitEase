from django.contrib import admin
from .models import Message, GroupChatRoom

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'group', 'message_type', 'created_at']
    list_filter = ['message_type', 'created_at', 'group']
    search_fields = ['sender__name', 'content', 'group__name']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(GroupChatRoom)
class GroupChatRoomAdmin(admin.ModelAdmin):
    list_display = ['group', 'created_at']
    readonly_fields = ['created_at']

