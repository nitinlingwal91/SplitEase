from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Activity
from groups.models import Group, GroupMember

@login_required
def activity_feed_view(request, group_id):
    group = get_object_or_404(Group, group_id=group_id)
    # Check membership
    if not GroupMember.objects.filter(group=group, user=request.user).exists():
        return redirect('groups:detail', group_id=group_id)
    activities = Activity.objects.filter(group=group).select_related('user').order_by('-timestamp')[:30]
    context = {
        'group': group,
        'activities': activities,
    }
    return render(request, 'activities/activity_feed.html', context)
