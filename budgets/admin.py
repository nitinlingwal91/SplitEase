from django.contrib import admin
from .models import BudgetPlan, BudgetItem, BudgetAlert

@admin.register(BudgetPlan)
class BudgetPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'group', 'period', 'start_date', 'end_date']
    list_filter = ['period', 'start_date', 'group']
    search_fields = ['name', 'group__name']

@admin.register(BudgetItem)
class BudgetItemAdmin(admin.ModelAdmin):
    list_display = ['category', 'budget', 'budget_amount', 'spent_amount']
    list_filter = ['budget', 'category']
    search_fields = ['category__name']

@admin.register(BudgetAlert)
class BudgetAlertAdmin(admin.ModelAdmin):
    list_display = ['budget_item', 'alert_type', 'created_at', 'is_read']
    list_filter = ['alert_type', 'is_read', 'created_at']
    search_fields = ['budget_item__category__name']
