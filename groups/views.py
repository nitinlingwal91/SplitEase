from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Group, GroupMember
from .forms import GroupForm, AddMemberForm
from users.models import User
from activities.models import Activity

@login_required
def create_group_view(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.owner = request.user
            group.save()
            # Add creator as admin member
            GroupMember.objects.create(group=group, user=request.user, is_admin=True)
            messages.success(request, f'Group "{group.name}" created successfully!')
            return redirect('groups:detail', group_id=group.group_id)
    else:
        form = GroupForm()
    return render(request, 'groups/create_group.html', {'form': form})


@login_required
def group_list_view(request):
    groups = request.user.group_memberships.all()
    return render(request, 'groups/group_list.html', {'groups': groups})


@login_required
def group_detail_view(request, group_id):
    group = get_object_or_404(Group, group_id=group_id)
    
    # Check if user is a member
    is_member = GroupMember.objects.filter(group=group, user=request.user).exists()
    is_admin = GroupMember.objects.filter(group=group, user=request.user, is_admin=True).exists()
    
    if not is_member:
        messages.error(request, 'You are not a member of this group.')
        return redirect('groups:list')
    
    members = GroupMember.objects.filter(group=group).select_related('user')
    expenses = group.expenses.all().order_by('-date')[:3]
    
    context = {
        'group': group,
        'members': members,
        'expenses': expenses,
        'is_owner': group.owner == request.user,
        'is_admin': is_admin,
    }
    return render(request, 'groups/group_detail.html', context)


@login_required
def add_member_view(request, group_id):
    group = get_object_or_404(Group, group_id=group_id)
    
    # Check if user is admin
    member = GroupMember.objects.filter(group=group, user=request.user, is_admin=True).first()
    if not member:
        messages.error(request, 'Only group admins can add members.')
        return redirect('groups:detail', group_id=group_id)
    
    if request.method == 'POST':
        form = AddMemberForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                if GroupMember.objects.filter(group=group, user=user).exists():
                    messages.warning(request, 'User is already a member.')
                else:
                    GroupMember.objects.create(group=group, user=user, is_admin=False)
                    messages.success(request, f'{user.name} added to group!')
                    
                    # Log activity
                    from activities.models import Activity
                    Activity.objects.create(
                        user=request.user,
                        group=group,
                        activity_type='member_joined',
                        description=f'Added {user.name} to the group'
                    )
            except User.DoesNotExist:
                messages.error(request, 'User with this email does not exist.')
            
            return redirect('groups:detail', group_id=group_id)
    else:
        form = AddMemberForm()
    
    return render(request, 'groups/add_member.html', {'form': form, 'group': group})

@login_required
def remove_member_view(request, group_id, member_id):
    group = get_object_or_404(Group, group_id=group_id)
    member_to_remove = get_object_or_404(GroupMember, member_id=member_id)
    
    # Check if user is admin
    admin_member = GroupMember.objects.filter(group=group, user=request.user, is_admin=True).first()
    if not admin_member:
        messages.error(request, 'Only group admins can remove members.')
        return redirect('groups:detail', group_id=group_id)
    
    # Can't remove owner
    if member_to_remove.user == group.owner:
        messages.error(request, 'Cannot remove group owner.')
        return redirect('groups:detail', group_id=group_id)
    
    # Can't remove self
    if member_to_remove.user == request.user:
        messages.error(request, 'You cannot remove yourself.')
        return redirect('groups:detail', group_id=group_id)
    
    member_name = member_to_remove.user.name
    member_to_remove.delete()
    messages.success(request, f'{member_name} removed from group.')
    
    # Log activity
    Activity.objects.create(
        user=request.user,
        group=group,
        activity_type='member_left',
        description=f'Removed {member_name} from the group'
    )
    
    return redirect('groups:detail', group_id=group_id)


@login_required
def delete_group_view(request, group_id):
    group = get_object_or_404(Group, group_id=group_id)
    if group.owner != request.user:
        messages.error(request, 'Only the group owner can delete the group.')
        return redirect('groups:detail', group_id=group_id)
    
    if request.method == 'POST':
        group_name = group.name
        group.delete()
        messages.success(request, f'Group "{group_name}" deleted successfully!')
        return redirect('groups:list')
    
    return render(request, 'groups/delete_group.html', {'group': group})

@login_required
def delete_group_view(request, group_id):
    group = get_object_or_404(Group, group_id=group_id)
    
    # Only allow group owner to delete the group
    if group.owner != request.user:
        messages.error(request, "You do not have permission to delete this group.")
        return redirect('groups:detail', group_id=group_id)
    
    if request.method == 'POST':
        group.delete()  # This cascades and deletes related data if foreign keys are set with cascade
        messages.success(request, f"Group '{group.name}' deleted successfully.")
        return redirect('groups:list')
    
    # Confirm deletion page
    return render(request, 'groups/group_confirm_delete.html', {'group': group})

def some_view(request, group_id):
    # your logic here
    return redirect('groups:detail', group_id=group_id)