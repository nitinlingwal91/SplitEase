from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from decimal import Decimal
from .models import Expense, ExpenseParticipant, Category
from .forms import ExpenseForm
from .filters import ExpenseFilter
from groups.models import Group, GroupMember
from .email_service import send_expense_notification
from activities.models import Activity
from settlements.algorithms import calculate_group_balances


@login_required
def add_expense_view(request, group_id):
    group = get_object_or_404(Group, group_id=group_id)
    if not GroupMember.objects.filter(group=group, user=request.user).exists():
        messages.error(request, 'You are not a member of this group.')
        return redirect('groups:detail', group_id=group_id)
    
    if request.method == 'POST':
        form = ExpenseForm(request.POST, group=group)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.group = group
            expense.payer = request.user
            expense.save()
            
            participants = form.cleaned_data['participants']
            share_amount = expense.calculate_equal_split(len(participants))
            
            for participant in participants:
                ExpenseParticipant.objects.create(
                    expense=expense,
                    user=participant,
                    share_amount=share_amount
                )
            
            # Recalculate balances
            calculate_group_balances(group)
            
            # Log activity
            Activity.objects.create(
                user=request.user,
                group=group,
                activity_type='expense_added',
                description=f'Added expense: {expense.description} ({expense.amount})',
                related_expense_id=expense.expense_id
            )
            
            # Send email notification
            send_expense_notification(expense)
            
            messages.success(request, 'Expense added successfully!')
            return redirect('groups:detail', group_id=group_id)
    else:
        form = ExpenseForm(group=group)
    
    return render(request, 'expenses/add_expense.html', {'form': form, 'group': group})


@login_required
def expense_list_view(request, group_id):
    group = get_object_or_404(Group, group_id=group_id)
    
    # Check membership
    if not GroupMember.objects.filter(group=group, user=request.user).exists():
        messages.error(request, 'You are not a member of this group.')
        return redirect('groups:list')
    
    expenses = Expense.objects.filter(group=group)
    
    # Apply filter
    expense_filter = ExpenseFilter(request.GET, queryset=expenses)
    filtered_expenses = expense_filter.qs
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        filtered_expenses = filtered_expenses.filter(
            Q(description__icontains=search_query) |
            Q(payer__name__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )
    
    context = {
        'group': group,
        'filter': expense_filter,
        'expenses': filtered_expenses,
        'search_query': search_query,
    }
    return render(request, 'expenses/expense_list.html', context)


@login_required
def expense_detail_view(request, expense_id):
    expense = get_object_or_404(Expense, expense_id=expense_id)
    participants = ExpenseParticipant.objects.filter(expense=expense)
    return render(request, 'expenses/expense_detail.html', {
        'expense': expense,
        'participants': participants
    })


@login_required
def delete_expense_view(request, expense_id):
    expense = get_object_or_404(Expense, expense_id=expense_id)
    if expense.payer != request.user:
        messages.error(request, 'You can only delete your own expenses.')
        return redirect('groups:detail', group_id=expense.group.group_id)
    
    if request.method == 'POST':
        group_id = expense.group.group_id
        expense.delete()
        
        # Recalculate balances
        from settlements.algorithms import calculate_group_balances
        calculate_group_balances(expense.group)
        
        messages.success(request, 'Expense deleted successfully!')
        return redirect('groups:detail', group_id=group_id)
    
    return render(request, 'expenses/delete_expense.html', {'expense': expense})


@login_required
def edit_expense_view(request, expense_id):
    """Edit an existing expense"""
    expense = get_object_or_404(Expense, expense_id=expense_id)
    group = expense.group
    
    # Check if user is member
    if not GroupMember.objects.filter(group=group, user=request.user).exists():
        messages.error(request, 'You are not a member of this group.')
        return redirect('groups:list')
    
    # Only expense creator (payer) can edit
    if expense.payer != request.user:
        messages.error(request, 'Only the person who created this expense can edit it.')
        return redirect('expenses:detail', expense_id=expense_id)
    
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense, group=group)
        if form.is_valid():
            # Save expense
            expense = form.save(commit=False)
            expense.save()
            
            # Clear existing participants
            ExpenseParticipant.objects.filter(expense=expense).delete()
            
            # Add new participants
            participants = form.cleaned_data['participants']
            share_amount = expense.calculate_equal_split(len(participants))
            
            for participant in participants:
                ExpenseParticipant.objects.create(
                    expense=expense,
                    user=participant.user,
                    share_amount=share_amount
                )
            
            # Recalculate group balances
            calculate_group_balances(group)
            
            # Log activity
            Activity.objects.create(
                user=request.user,
                group=group,
                activity_type='expense_added',
                description=f'Updated expense: {expense.description} ({expense.amount})',
                related_expense_id=expense.expense_id
            )
            
            messages.success(request, 'Expense updated successfully!')
            return redirect('expenses:detail', expense_id=expense_id)
    else:
        # Pre-populate form with existing data
        form = ExpenseForm(instance=expense, group=group)
        # Pre-select existing participants
        existing_participants = expense.participants.all()
        form.fields['participants'].initial = [p.member_id for p in GroupMember.objects.filter(
            user__in=[ep.user for ep in existing_participants]
        )]
    
    context = {
        'form': form,
        'group': group,
        'expense': expense,
        'is_edit': True,
    }
    return render(request, 'expenses/add_expense.html', context)