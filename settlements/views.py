from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from groups.models import Group, GroupMember
from .models import Settlement
from .algorithms import optimize_settlements, get_settlement_summary, calculate_group_balances
from activities.models import Activity


@login_required
def balance_summary_view(request):
    """Show user's overall balance summary across all groups"""
    user = request.user
    groups = user.group_memberships.all()
    
    total_owes = 0
    total_owed = 0
    balances = []
    
    for membership in groups:
        group = membership.group
        summary = get_settlement_summary(group, user)
        
        if summary['owes'] or summary['owed']:
            balances.append({
                'group': group,
                'summary': summary,
            })
        
        total_owes += summary['total_owes']
        total_owed += summary['total_owed']
    
    net_balance = total_owed - total_owes
    
    context = {
        'balances': balances,
        'total_owes': total_owes,
        'total_owed': total_owed,
        'net_balance': net_balance,
    }
    return render(request, 'settlements/balance_summary.html', context)

@login_required
def group_balance_view(request, group_id):
    """Show balance for a specific group"""
    group = get_object_or_404(Group, group_id=group_id)
    
    # Check membership
    if not GroupMember.objects.filter(group=group, user=request.user).exists():
        messages.error(request, 'You are not a member of this group.')
        return redirect('groups:list')
    
    summary = get_settlement_summary(group, request.user)
    
    context = {
        'group': group,
        'summary': summary,
    }
    return render(request, 'settlements/group_balance.html', context)


@login_required
def optimize_settlements_view(request, group_id):
    """Generate and display optimized settlement plan"""
    group = get_object_or_404(Group, group_id=group_id)
    
    # Check membership
    if not GroupMember.objects.filter(group=group, user=request.user).exists():
        messages.error(request, 'You are not a member of this group.')
        return redirect('groups:list')
    
    # Recalculate balances to ensure accuracy
    calculate_group_balances(group)
    
    # Generate optimized settlements
    optimized_settlements = optimize_settlements(group)
    
    # Handle POST request (when user confirms)
    if request.method == 'POST' and 'confirm' in request.POST:
        try:
            # Clear existing pending settlements
            old_count = Settlement.objects.filter(group=group, is_completed=False).count()
            Settlement.objects.filter(group=group, is_completed=False).delete()
            
            # Save new optimized settlements
            created_settlements = []
            for settlement in optimized_settlements:
                settlement.save()
                created_settlements.append(settlement)
            
            # Log activity
            Activity.objects.create(
                user=request.user,
                group=group,
                activity_type='settlement_created',
                description=f'Created {len(created_settlements)} optimized settlements (replaced {old_count} previous)'
            )
            
            messages.success(request, f'{len(created_settlements)} optimized settlements created successfully!')
            return redirect('settlements:settlement_list', group_id=group_id)
        
        except Exception as e:
            messages.error(request, f'Error creating settlements: {str(e)}')
            return redirect('settlements:optimize', group_id=group_id)
    
    # GET request - show preview
    context = {
        'group': group,
        'settlements': optimized_settlements,
        'total_transactions': len(optimized_settlements),
    }
    return render(request, 'settlements/optimize.html', context)


@login_required
def settlement_list_view(request, group_id):
    """Show all settlements for a group"""
    group = get_object_or_404(Group, group_id=group_id)
    
    # Check membership
    if not GroupMember.objects.filter(group=group, user=request.user).exists():
        messages.error(request, 'You are not a member of this group.')
        return redirect('groups:list')
    
    pending_settlements = Settlement.objects.filter(group=group, is_completed=False)
    completed_settlements = Settlement.objects.filter(group=group, is_completed=True)
    
    context = {
        'group': group,
        'pending_settlements': pending_settlements,
        'completed_settlements': completed_settlements,
    }
    return render(request, 'settlements/settlement_list.html', context)



@login_required
def mark_settlement_complete_view(request, settlement_id):
    """Mark a settlement as completed"""
    settlement = get_object_or_404(Settlement, settlement_id=settlement_id)
    
    # Only payer or payee can mark as complete
    if request.user not in [settlement.payer, settlement.payee]:
        messages.error(request, 'Only payer or payee can mark settlement as complete.')
        return redirect('settlements:settlement_list', group_id=settlement.group.group_id)
    
    if request.method == 'POST':
        from django.utils import timezone
        
        settlement.is_completed = True
        settlement.completed_at = timezone.now()
        settlement.save()
        
        messages.success(request, f'Settlement marked as complete!')
        
        # Log activity
        Activity.objects.create(
            user=request.user,
            group=settlement.group,
            activity_type='settlement_completed',
            description=f'{settlement.payer.name} paid {settlement.amount} {settlement.group.currency} to {settlement.payee.name}'
        )
    
    return redirect('settlements:settlement_list', group_id=settlement.group.group_id)

