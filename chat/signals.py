from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_out
from .models import UserActivity


@receiver(user_logged_out)
def mark_user_offline(sender, request, user, **kwargs):
    """Mark user as offline in all groups when they logout"""
    UserActivity.objects.filter(user=user).update(
        is_online=False
    )
