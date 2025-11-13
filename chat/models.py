from django.db import models
from django.utils import timezone
from users.models import User
from groups.models import Group


class Message(models.Model):
    MESSAGE_TYPES = [
        ('text', 'Text'),
        ('comment', 'Comment on Expense'),
        ('system', 'System Message'),
    ]
    
    message_id = models.AutoField(primary_key=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages_sent')
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='text')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_edited = models.BooleanField(default=False)
    related_expense_id = models.IntegerField(null=True, blank=True)
    
    class Meta:
        db_table = 'chat_messages'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.sender.name}: {self.content[:50]}"


class GroupChatRoom(models.Model):
    """Real-time chat room for each group"""
    room_id = models.AutoField(primary_key=True)
    group = models.OneToOneField(Group, on_delete=models.CASCADE, related_name='chat_room')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'chat_rooms'
    
    def __str__(self):
        return f"Chat - {self.group.name}"


class UserActivity(models.Model):
    """Track user activity in chat"""
    activity_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_activities')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='user_activities')
    last_seen = models.DateTimeField(auto_now=True)
    is_online = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'chat_user_activity'
        unique_together = ['user', 'group']
        indexes = [
            models.Index(fields=['group', 'is_online', 'last_seen']),
        ]
    
    def __str__(self):
        return f"{self.user.name} - {self.group.name}"
