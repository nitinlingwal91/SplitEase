from django.test import TestCase
from django.core.exceptions import ValidationError
from decimal import Decimal
from users.models import User
from groups.models import Group
from expenses.models import Expense, ExpenseParticipant


class TestExpenseCreation(TestCase):
    """TC13: Expense Creation"""
    
    def setUp(self):
        self.owner = User.objects.create_user(
            email='expowner@example.com',
            password='Pass123',
            name='Expense Owner'
        )
        self.owner.save()
        
        self.group = Group.objects.create(
            name='Expense Group',
            owner=self.owner
        )
        self.group.save()
    
    def test_expense_creation_valid(self):
        """TC13.1: Create expense with valid data"""
        expense = Expense.objects.create(
            group=self.group,
            description='Dinner',
            amount=Decimal('100.00'),
            payer=self.owner,
            split_type='equal'
        )
        expense.save()
        self.assertIsNotNone(expense.expense_id)
        self.assertEqual(expense.description, 'Dinner')
        self.assertEqual(expense.amount, Decimal('100.00'))
    
    def test_expense_description_required(self):
        """TC13.2: Description is mandatory"""
        with self.assertRaises((ValidationError, Exception)):
            expense = Expense(
                group=self.group,
                description='',
                amount=Decimal('50.00'),
                payer=self.owner
            )
            expense.full_clean()
            expense.save()
    
    def test_expense_negative_amount_rejected(self):
        """TC13.4: Negative amount rejected"""
        expense = Expense(
            group=self.group,
            description='Negative',
            amount=Decimal('-50.00'),
            payer=self.owner
        )
        with self.assertRaises((ValidationError, Exception)):
            expense.full_clean()
            expense.save()
    
    def test_expense_zero_amount_rejected(self):
        """TC13.5: Zero amount rejected"""
        expense = Expense(
            group=self.group,
            description='Zero',
            amount=Decimal('0.00'),
            payer=self.owner
        )
        with self.assertRaises((ValidationError, Exception)):
            expense.full_clean()
            expense.save()
    
    def test_expense_decimal_precision(self):
        """TC13.6: Decimal precision"""
        expense = Expense.objects.create(
            group=self.group,
            description='Precision Test',
            amount=Decimal('99.99'),
            payer=self.owner
        )
        expense.save()
        self.assertEqual(expense.amount, Decimal('99.99'))
    
    def test_expense_creation_minimum_amount(self):
        """TC13.7: Minimum amount allowed"""
        expense = Expense.objects.create(
            group=self.group,
            description='Min Amount',
            amount=Decimal('0.01'),
            payer=self.owner
        )
        expense.save()
        self.assertEqual(expense.amount, Decimal('0.01'))
    
    def test_expense_creation_maximum_amount(self):
        """TC13.8: Maximum amount allowed"""
        expense = Expense.objects.create(
            group=self.group,
            description='Max Amount',
            amount=Decimal('999999.99'),
            payer=self.owner
        )
        expense.save()
        self.assertIsNotNone(expense.expense_id)
    
    def test_expense_timestamps(self):
        """TC13.9: Expense timestamps"""
        expense = Expense.objects.create(
            group=self.group,
            description='Timestamp Test',
            amount=Decimal('50.00'),
            payer=self.owner
        )
        expense.save()
        self.assertIsNotNone(expense.created_at)


class TestEqualSplit(TestCase):
    """TC14: Equal Split Calculation"""
    
    def setUp(self):
        self.owner = User.objects.create_user(
            email='split1@example.com',
            password='Pass123',
            name='Split User 1'
        )
        self.owner.save()
        
        self.user2 = User.objects.create_user(
            email='split2@example.com',
            password='Pass123',
            name='Split User 2'
        )
        self.user2.save()
        
        self.group = Group.objects.create(
            name='Split Group',
            owner=self.owner
        )
        self.group.save()
    
    def test_equal_split_two_people(self):
        """TC14.1: Equal split between 2 people"""
        expense = Expense.objects.create(
            group=self.group,
            description='Split Test',
            amount=Decimal('100.00'),
            payer=self.owner,
            split_type='equal'
        )
        expense.save()
        
        ExpenseParticipant.objects.create(
            expense=expense,
            user=self.owner,
            amount=Decimal('50.00')
        ).save()
        
        ExpenseParticipant.objects.create(
            expense=expense,
            user=self.user2,
            amount=Decimal('50.00')
        ).save()
        
        participants = ExpenseParticipant.objects.filter(expense=expense)
        self.assertEqual(participants.count(), 2)
        for p in participants:
            self.assertEqual(p.amount, Decimal('50.00'))
    
    def test_equal_split_three_people(self):
        """TC14.2: Equal split between 3 people"""
        user3 = User.objects.create_user(
            email='split3@example.com',
            password='Pass123',
            name='Split User 3'
        )
        user3.save()
        
        expense = Expense.objects.create(
            group=self.group,
            description='Three Way Split',
            amount=Decimal('99.00'),
            payer=self.owner,
            split_type='equal'
        )
        expense.save()
        
        amount = Decimal('33.00')
        ExpenseParticipant.objects.create(expense=expense, user=self.owner, amount=amount).save()
        ExpenseParticipant.objects.create(expense=expense, user=self.user2, amount=amount).save()
        ExpenseParticipant.objects.create(expense=expense, user=user3, amount=amount).save()
        
        total = sum([p.amount for p in ExpenseParticipant.objects.filter(expense=expense)])
        self.assertEqual(total, Decimal('99.00'))


class TestExpenseEditDelete(TestCase):
    """TC17: Expense Editing and Deletion"""
    
    def setUp(self):
        self.owner = User.objects.create_user(
            email='edit@example.com',
            password='Pass123',
            name='Edit User'
        )
        self.owner.save()
        
        self.group = Group.objects.create(
            name='Edit Group',
            owner=self.owner
        )
        self.group.save()
        
        self.expense = Expense.objects.create(
            group=self.group,
            description='Original',
            amount=Decimal('100.00'),
            payer=self.owner
        )
        self.expense.save()
    
    def test_expense_update_description(self):
        """TC17.1: Update description"""
        self.expense.description = 'Updated Description'
        self.expense.save()
        updated = Expense.objects.get(expense_id=self.expense.expense_id)
        self.assertEqual(updated.description, 'Updated Description')
    
    def test_expense_update_amount(self):
        """TC17.2: Update amount"""
        self.expense.amount = Decimal('150.00')
        self.expense.save()
        updated = Expense.objects.get(expense_id=self.expense.expense_id)
        self.assertEqual(updated.amount, Decimal('150.00'))
    
    def test_expense_deletion(self):
        """TC17.3: Delete expense"""
        expense_id = self.expense.expense_id
        self.expense.delete()
        self.assertFalse(Expense.objects.filter(expense_id=expense_id).exists())
    
    def test_delete_expense_removes_participants(self):
        """TC17.4: Deleting removes participants"""
        ExpenseParticipant.objects.create(
            expense=self.expense,
            user=self.owner,
            amount=Decimal('100.00')
        ).save()
        
        expense_id = self.expense.expense_id
        self.expense.delete()
        
        self.assertFalse(ExpenseParticipant.objects.filter(expense_id=expense_id).exists())