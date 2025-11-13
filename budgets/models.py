from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from groups.models import Group
from expenses.models import Category
from decimal import Decimal


class BudgetPlan(models.Model):
    PERIOD_CHOICES = [
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ]
    
    budget_id = models.AutoField(primary_key=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='budgets')
    name = models.CharField(max_length=100)
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES, default='monthly')
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'budget_plans'
    
    def __str__(self):
        return f"{self.group.name} - {self.name}"


class BudgetItem(models.Model):
    item_id = models.AutoField(primary_key=True)
    budget = models.ForeignKey(BudgetPlan, on_delete=models.CASCADE, related_name='items')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    budget_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    spent_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0'))]
    )
    alert_percentage = models.IntegerField(default=80)  # Alert at 80% spent
    
    class Meta:
        db_table = 'budget_items'
    
    def get_percentage_spent(self):
        if self.budget_amount == 0:
            return 0
        return (self.spent_amount / self.budget_amount) * 100
    
    def is_over_budget(self):
        return self.spent_amount > self.budget_amount
    
    def is_alert_threshold(self):
        return self.get_percentage_spent() >= self.alert_percentage
    
    def remaining_budget(self):
        return max(self.budget_amount - self.spent_amount, Decimal('0'))
    
    def __str__(self):
        return f"{self.category.name} - {self.budget_amount}"


class BudgetAlert(models.Model):
    ALERT_TYPES = [
        ('threshold', 'Threshold Reached'),
        ('over', 'Over Budget'),
    ]
    
    alert_id = models.AutoField(primary_key=True)
    budget_item = models.ForeignKey(BudgetItem, on_delete=models.CASCADE, related_name='alerts')
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'budget_alerts'
        ordering = ['-created_at']

