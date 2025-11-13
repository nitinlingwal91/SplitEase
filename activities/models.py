from django.db import models
from django.utils import timezone
from users.models import User
from groups.models import Group

class Activity(models.Model):
    ACTIVITY_TYPES = [
        ('expense_added', 'Expense Added'),
        ('expense_deleted', 'Expense Deleted'),
        ('settlement_created', 'Settlement Created'),
        ('settlement_completed', 'Settlement Completed'),
        ('member_joined', 'Member Joined'),
        ('member_left', 'Member Left'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPES)
    description = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    related_expense_id = models.IntegerField(null=True, blank=True)
    
    class Meta:
        db_table = 'activities'
        ordering = ['-timestamp']
        verbose_name_plural = 'Activities'
    
    def __str__(self):
        return f"{self.user.name} - {self.get_activity_type_display()}"
