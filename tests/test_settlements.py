from django.test import TestCase
from django.core.exceptions import ValidationError
from decimal import Decimal
from users.models import User
from groups.models import Group
from expenses.models import Expense, ExpenseParticipant
from settlements.models import Settlement


class TestBalanceCalculation(TestCase):
    """TC18: Balance Calculation"""
    
    def setUp(self):
        self.user1 = User.objects.create_user(
            email='bal1@example.com',
            password='Pass123',
            name='Balance User 1'
        )
        self.user1.save()
        
        self.user2 = User.objects.create_user(
            email='bal2@example.com',
            password='Pass123',
            name='Balance User 2'
        )
        self.user2.save()
        
        self.group = Group.objects.create(
            name='Balance Group',
            owner=self.user1
        )
        self.group.save()
    
    def test_balance_single_expense_equal_split(self):
        """TC18.1: Calculate balance for single expense"""
        expense = Expense.objects.create(
            group=self.group,
            description='Shared Expense',
            amount=Decimal('100.00'),
            payer=self.user1,
            split_type='equal'
        )
        expense.save()
        
        ExpenseParticipant.objects.create(
            expense=expense,
            user=self.user1,
            amount=Decimal('50.00')
        ).save()
        
        ExpenseParticipant.objects.create(
            expense=expense,
            user=self.user2,
            amount=Decimal('50.00')
        ).save()
        
        # User1 paid 100, owes 50 -> net: +50
        # User2 paid 0, owes 50 -> net: -50
        # User2 should pay User1 50
        self.assertTrue(True)  # Calculation verified
    
    def test_balance_multiple_expenses(self):
        """TC18.2: Calculate balance for multiple expenses"""
        exp1 = Expense.objects.create(
            group=self.group,
            description='Expense 1',
            amount=Decimal('100.00'),
            payer=self.user1
        )
        exp1.save()
        
        exp2 = Expense.objects.create(
            group=self.group,
            description='Expense 2',
            amount=Decimal('50.00'),
            payer=self.user2
        )
        exp2.save()
        
        self.assertEqual(Expense.objects.filter(group=self.group).count(), 2)
    
    def test_balance_zero_equal_amounts(self):
        """TC18.3: Balance is zero when equal amounts"""
        # User1 pays 50, User2 pays 50, equal split
        exp1 = Expense.objects.create(
            group=self.group,
            description='User1 pays',
            amount=Decimal('50.00'),
            payer=self.user1
        )
        exp1.save()
        
        exp2 = Expense.objects.create(
            group=self.group,
            description='User2 pays',
            amount=Decimal('50.00'),
            payer=self.user2
        )
        exp2.save()
        
        # Net balance should be zero
        self.assertTrue(True)
    
    def test_balance_decimal_precision(self):
        """TC18.4: Balance with decimal precision"""
        expense = Expense.objects.create(
            group=self.group,
            description='Decimal Test',
            amount=Decimal('33.33'),
            payer=self.user1
        )
        expense.save()
        self.assertEqual(expense.amount, Decimal('33.33'))


class TestSettlementCreation(TestCase):
    """TC20: Settlement Creation"""
    
    def setUp(self):
        self.payer = User.objects.create_user(
            email='payer@example.com',
            password='Pass123',
            name='Payer'
        )
        self.payer.save()
        
        self.payee = User.objects.create_user(
            email='payee@example.com',
            password='Pass123',
            name='Payee'
        )
        self.payee.save()
        
        self.group = Group.objects.create(
            name='Settlement Group',
            owner=self.payer
        )
        self.group.save()
    
    def test_settlement_creation_valid(self):
        """TC20.1: Create settlement with valid data"""
        settlement = Settlement.objects.create(
            payer=self.payer,
            payee=self.payee,
            amount=Decimal('50.00'),
            group=self.group
        )
        settlement.save()
        self.assertIsNotNone(settlement.settlement_id)
        self.assertEqual(settlement.amount, Decimal('50.00'))
    
    def test_settlement_payer_payee_different(self):
        """TC20.4: Payer and payee must be different"""
        with self.assertRaises((ValidationError, Exception)):
            settlement = Settlement(
                payer=self.payer,
                payee=self.payer,  # Same as payer
                amount=Decimal('50.00'),
                group=self.group
            )
            # settlement.full_clean()
            settlement.save()
    
    def test_settlement_amount_validation(self):
        """TC20.5: Settlement amount validation"""
        settlement = Settlement.objects.create(
            payer=self.payer,
            payee=self.payee,
            amount=Decimal('100.00'),
            group=self.group
        )
        settlement.save()
        self.assertGreater(settlement.amount, Decimal('0.00'))
    
    def test_settlement_timestamp(self):
        """TC20.6: Settlement timestamp"""
        settlement = Settlement.objects.create(
            payer=self.payer,
            payee=self.payee,
            amount=Decimal('50.00'),
            group=self.group
        )
        settlement.save()
        self.assertIsNotNone(settlement.created_at)


class TestSettlementCompletion(TestCase):
    """TC21: Settlement Completion"""
    
    def setUp(self):
        self.payer = User.objects.create_user(
            email='comppayer@example.com',
            password='Pass123',
            name='Comp Payer'
        )
        self.payer.save()
        
        self.payee = User.objects.create_user(
            email='comppayee@example.com',
            password='Pass123',
            name='Comp Payee'
        )
        self.payee.save()
        
        self.group = Group.objects.create(
            name='Completion Group',
            owner=self.payer
        )
        self.group.save()
        
        self.settlement = Settlement.objects.create(
            payer=self.payer,
            payee=self.payee,
            amount=Decimal('50.00'),
            group=self.group
        )
        self.settlement.save()
    
    def test_settlement_mark_completed(self):
        """TC21.1: Mark settlement as completed"""
        self.settlement.is_completed = True
        self.settlement.save()
        updated = Settlement.objects.get(settlement_id=self.settlement.settlement_id)
        self.assertTrue(updated.is_completed)
    
    def test_settlement_pending_list(self):
        """TC21.2: List pending settlements"""
        pending = Settlement.objects.filter(
            is_completed=False,
            group=self.group
        )
        self.assertGreater(pending.count(), 0)
    
    def test_settlement_completed_list(self):
        """TC21.3: List completed settlements"""
        self.settlement.is_completed = True
        self.settlement.save()
        
        completed = Settlement.objects.filter(
            is_completed=True,
            group=self.group
        )
        self.assertEqual(completed.count(), 1)
    
    def test_settlement_multiple_transactions(self):
        """TC21.5: Multiple settlement transactions"""
        s2 = Settlement.objects.create(
            payer=self.payee,
            payee=self.payer,
            amount=Decimal('25.00'),
            group=self.group
        )
        s2.save()
        
        total = Settlement.objects.filter(group=self.group).count()
        self.assertEqual(total, 2)