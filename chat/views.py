from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from datetime import timedelta
from groups.models import Group, GroupMember
from .models import Message, UserActivity


@login_required
def group_chat_view(request, group_id):
    """Display group chat"""
    group = get_object_or_404(Group, group_id=group_id)
    
    # Check membership
    if not GroupMember.objects.filter(group=group, user=request.user).exists():
        messages.error(request, 'You are not a member of this group.')
        return redirect('groups:list')
    
    # Update user activity - Mark as online
    UserActivity.objects.update_or_create(
        user=request.user,
        group=group,
        defaults={
            'is_online': True,
            'last_seen': timezone.now()
        }
    )
    
    # Get recent messages
    recent_messages = Message.objects.filter(group=group).order_by('-created_at')[:100]
    
    # Get online members (last seen in 2 minutes)
    two_min_ago = timezone.now() - timedelta(minutes=2)
    online_members = UserActivity.objects.filter(
        group=group,
        last_seen__gte=two_min_ago
    ).select_related('user')
    
    context = {
        'group': group,
        'messages': reversed(recent_messages),
        'online_members': online_members,
    }
    return render(request, 'chat/group_chat.html', context)


@login_required
@require_http_methods(["POST"])
def send_message_view(request, group_id):
    """Send a message"""
    group = get_object_or_404(Group, group_id=group_id)
    
    # Check membership
    if not GroupMember.objects.filter(group=group, user=request.user).exists():
        return JsonResponse({'error': 'Not authorized'}, status=403)
    
    content = request.POST.get('message', '').strip()
    
    if not content:
        return JsonResponse({'error': 'Message cannot be empty'}, status=400)
    
    if len(content) > 1000:
        return JsonResponse({'error': 'Message too long'}, status=400)
    
    # Update user activity
    UserActivity.objects.update_or_create(
        user=request.user,
        group=group,
        defaults={
            'is_online': True,
            'last_seen': timezone.now()
        }
    )
    
    # Create message
    message = Message.objects.create(
        group=group,
        sender=request.user,
        message_type='text',
        content=content
    )
    
    return JsonResponse({
        'success': True,
        'message': {
            'id': message.message_id,
            'sender': message.sender.name,
            'sender_id': message.sender.user_id,
            'content': message.content,
            'timestamp': message.created_at.isoformat(),
        }
    })


@login_required
def get_messages_view(request, group_id):
    """Get messages as JSON"""
    group = get_object_or_404(Group, group_id=group_id)
    
    # Check membership
    if not GroupMember.objects.filter(group=group, user=request.user).exists():
        return JsonResponse({'error': 'Not authorized'}, status=403)
    
    # Update user activity
    UserActivity.objects.update_or_create(
        user=request.user,
        group=group,
        defaults={
            'is_online': True,
            'last_seen': timezone.now()
        }
    )
    
    # Get messages since last_id
    last_id = request.GET.get('last_id', 0)
    messages_list = Message.objects.filter(
        group=group,
        message_id__gt=last_id
    ).order_by('created_at')[:50]
    
    data = {
        'messages': [
            {
                'id': msg.message_id,
                'sender': msg.sender.name,
                'sender_id': msg.sender.user_id,
                'content': msg.content,
                'timestamp': msg.created_at.isoformat(),
                'type': msg.message_type,
            }
            for msg in messages_list
        ]
    }
    
    return JsonResponse(data)


@login_required
def get_online_members_view(request, group_id):
    """Get online members - last active in 2 minutes AND is_online=True"""
    group = get_object_or_404(Group, group_id=group_id)
    
    # Check membership
    if not GroupMember.objects.filter(group=group, user=request.user).exists():
        return JsonResponse({'error': 'Not authorized'}, status=403)
    
    # Get online members (last seen in 2 minutes AND is_online=True)
    two_min_ago = timezone.now() - timedelta(minutes=2)
    online_activities = UserActivity.objects.filter(
        group=group,
        last_seen__gte=two_min_ago,
        is_online=True  # ADD THIS LINE
    ).select_related('user')
    
    return JsonResponse({
        'members': [
            {
                'user__user_id': activity.user.user_id,
                'user__name': activity.user.name,
            }
            for activity in online_activities
        ]
    })
