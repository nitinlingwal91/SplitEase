from django.db import models
from django.utils import timezone
from users.models import User


class Group(models.Model):
    group_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    currency = models.CharField(max_length=3, default='USD')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_groups')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'groups'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_total_members(self):
        return self.members.count()


class GroupMember(models.Model):
    member_id = models.AutoField(primary_key=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_memberships')
    joined_date = models.DateField(default=timezone.now)
    is_admin = models.BooleanField(default=False)

    class Meta:
        db_table = 'group_members'
        unique_together = ['group', 'user']

    def __str__(self):
        return f"{self.user.name} - {self.group.name}"
