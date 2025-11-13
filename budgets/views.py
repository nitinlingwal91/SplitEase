from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from groups.models import Group, GroupMember
from .models import BudgetPlan, BudgetItem, BudgetAlert
from expenses.models import Expense, Category
from decimal import Decimal
from datetime import datetime


@login_required
def budget_list_view(request, group_id):
    """List all budgets for a group"""
    group = get_object_or_404(Group, group_id=group_id)
    
    if not GroupMember.objects.filter(group=group, user=request.user).exists():
        messages.error(request, 'You are not a member of this group.')
        return redirect('groups:list')
    
    budgets = BudgetPlan.objects.filter(group=group)
    
    context = {
        'group': group,
        'budgets': budgets,
    }
    return render(request, 'budgets/budget_list.html', context)


@login_required
def budget_detail_view(request, budget_id):
    """View budget details and spending progress"""
    budget = get_object_or_404(BudgetPlan, budget_id=budget_id)
    group = budget.group
    
    if not GroupMember.objects.filter(group=group, user=request.user).exists():
        messages.error(request, 'You are not a member of this group.')
        return redirect('groups:list')
    
    # Calculate spent amounts
    for item in budget.items.all():
        expenses = Expense.objects.filter(
            group=group,
            category=item.category,
            date__range=[budget.start_date, budget.end_date]
        )
        spent = expenses.aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
        item.spent_amount = spent
        item.save()
    
    # Get alerts
    alerts = BudgetAlert.objects.filter(budget_item__budget=budget)
    
    context = {
        'budget': budget,
        'group': group,
        'items': budget.items.all(),
        'alerts': alerts,
    }
    return render(request, 'budgets/budget_detail.html', context)


@login_required
def create_budget_view(request, group_id):
    """Create new budget"""
    group = get_object_or_404(Group, group_id=group_id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        period = request.POST.get('period')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        
        budget = BudgetPlan.objects.create(
            group=group,
            name=name,
            period=period,
            start_date=start_date,
            end_date=end_date
        )
        
        # Add budget items for each category
        categories = Category.objects.all()
        for category in categories:
            amount = request.POST.get(f'category_{category.category_id}')
            if amount:
                BudgetItem.objects.create(
                    budget=budget,
                    category=category,
                    budget_amount=Decimal(amount)
                )
        
        messages.success(request, 'Budget created successfully!')
        return redirect('budgets:detail', budget_id=budget.budget_id)
    
    categories = Category.objects.all()
    context = {
        'group': group,
        'categories': categories,
    }
    return render(request, 'budgets/create_budget.html', context)


def update_budget_spending(group_id):
    """Background task to update budget spending"""
    from expenses.models import Expense
    
    budgets = BudgetPlan.objects.filter(group_id=group_id)
    
    for budget in budgets:
        for item in budget.items.all():
            expenses = Expense.objects.filter(
                group_id=group_id,
                category=item.category,
                date__range=[budget.start_date, budget.end_date]
            )
            spent = expenses.aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
            
            old_spent = item.spent_amount
            item.spent_amount = spent
            item.save()
            
            # Create alert if threshold reached
            if item.get_percentage_spent() >= item.alert_percentage and old_spent < spent:
                BudgetAlert.objects.create(
                    budget_item=item,
                    alert_type='threshold',
                    message=f'Budget for {item.category.name} is {item.get_percentage_spent():.1f}% spent'
                )
            
            # Create alert if over budget
            if item.is_over_budget() and old_spent <= item.budget_amount:
                BudgetAlert.objects.create(
                    budget_item=item,
                    alert_type='over',
                    message=f'Budget for {item.category.name} exceeded!'
                )
