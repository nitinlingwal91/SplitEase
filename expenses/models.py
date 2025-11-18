from django.db import models
from django.utils import timezone
from decimal import Decimal
from users.models import User
from groups.models import Group
from django.core.exceptions import ValidationError

class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'categories'

    def __str__(self):
        return self.name


class Expense(models.Model):
    SPLIT_TYPES = [
        ('equal', 'Equal Split'),
        ('exact', 'Exact Amount'),
        ('percentage', 'Percentage'),
    ]

    expense_id = models.AutoField(primary_key=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='expenses')
    payer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='paid_expenses')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255)
    date = models.DateField(default=timezone.now)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    split_type = models.CharField(max_length=10, choices=SPLIT_TYPES, default='equal')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'expenses'
        ordering = ['-date']

    def __str__(self):
        return f"{self.description} - {self.amount}"
    
    def clean(self):
        """Validate expense data"""
        if not self.description or self.description.strip() == '':
            raise ValidationError('Description is required.')
        if self.amount <= 0:
            raise ValidationError('Amount must be positive and greater than zero.')

    def save(self, *args, **kwargs):
        """Override save to call clean"""
        self.full_clean()
        super().save(*args, **kwargs)
    
    def calculate_equal_split(self, num_participants):
        if num_participants == 0:
            return Decimal('0.00')
        return (self.amount / num_participants).quantize(Decimal('0.01'))


class ExpenseParticipant(models.Model):
    participant_id = models.AutoField(primary_key=True)
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expense_participations')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    share_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    is_settled = models.BooleanField(default=False)

    class Meta:
        db_table = 'expense_participants'
        unique_together = ['expense', 'user']

    def __str__(self):
        return f"{self.user.name} - {self.amount}"
