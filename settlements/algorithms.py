from decimal import Decimal
from collections import defaultdict
from .models import Balance, Settlement
from users.models import User
from groups.models import GroupMember
from expenses.models import Expense, ExpenseParticipant


class SettlementOptimizer:
    def __init__(self, group):
        self.group = group
        self.balances = defaultdict(Decimal)
    
    def calculate_net_balances(self):
        balance_records = Balance.objects.filter(group=self.group)
        for balance in balance_records:
            self.balances[balance.user1.user_id] -= balance.amount
            self.balances[balance.user2.user_id] += balance.amount
        return self.balances
    
    def minimize_transactions(self):
        self.calculate_net_balances()
        debtors = []
        creditors = []
        
        for user_id, balance in self.balances.items():
            if balance < 0:
                debtors.append([user_id, abs(balance)])
            elif balance > 0:
                creditors.append([user_id, balance])
        
        debtors.sort(key=lambda x: x, reverse=True)
        creditors.sort(key=lambda x: x, reverse=True)
        
        settlements = []
        i = j = 0
        
        while i < len(debtors) and j < len(creditors):
            debtor_id, debt_amount = debtors[i]
            creditor_id, credit_amount = creditors[j]
            
            transfer_amount = min(debt_amount, credit_amount)
            
            settlements.append({
                'payer_id': debtor_id,
                'payee_id': creditor_id,
                'amount': transfer_amount
            })
            
            debtors[i] -= transfer_amount
            creditors[j] -= transfer_amount
            
            if debtors[i] == 0:
                i += 1
            if creditors[j] == 0:
                j += 1
        
        return settlements
    
    def create_settlement_records(self):
        optimized_settlements = self.minimize_transactions()
        created_settlements = []
        
        for settlement_data in optimized_settlements:
            payer = User.objects.get(user_id=settlement_data['payer_id'])
            payee = User.objects.get(user_id=settlement_data['payee_id'])
            
            settlement = Settlement.objects.create(
                payer=payer,
                payee=payee,
                amount=settlement_data['amount'],
                group=self.group,
                status='pending'
            )
            created_settlements.append(settlement)
        
        return created_settlements


def calculate_group_balances(group):
    """
    Calculate and update balance records for all members in a group.
    This is called after expenses are added or modified.
    """
    # Clear existing balances
    Balance.objects.filter(group=group).delete()
    
    # Get all expenses for this group
    expenses = group.expenses.all()
    
    # Calculate net balance for each user
    balances = defaultdict(Decimal)
    
    for expense in expenses:
        # Payer gets credited
        balances[expense.payer.user_id] += Decimal(str(expense.amount))
        
        # Participants get debited
        participants = expense.participants.all()
        for participant in participants:
            balances[participant.user.user_id] -= Decimal(str(participant.share_amount))
    
    # Create Balance records for each pair where money is owed
    members = GroupMember.objects.filter(group=group)
    member_dict = {m.user.user_id: m.user for m in members}
    
    for user_id, balance in balances.items():
        if balance > 0:  # User is owed money
            for other_id, other_balance in balances.items():
                if other_balance < 0 and user_id != other_id:  # Other user owes money
                    amount_owed = min(balance, abs(other_balance))
                    if amount_owed > 0:
                        Balance.objects.create(
                            group=group,
                            user1=member_dict[other_id],  # Debtor
                            user2=member_dict[user_id],   # Creditor
                            amount=amount_owed
                        )
                        balances[user_id] -= amount_owed
                        balances[other_id] += amount_owed
                        balance = balances[user_id]
                        if balance <= 0:
                            break
                        
def optimize_settlements(group):
    """
    Generate optimized settlement transactions to minimize the number of payments.
    """
    balances = Balance.objects.filter(group=group)
    
    # Calculate net balance for each user
    net_balances = defaultdict(Decimal)
    
    for balance in balances:
        net_balances[balance.user1.user_id] -= balance.amount  # Owes
        net_balances[balance.user2.user_id] += balance.amount  # Owed
    
    # Separate debtors and creditors
    debtors = []   # List of [user_id, amount_owed]
    creditors = []  # List of [user_id, amount_owed]
    
    for user_id, balance in net_balances.items():
        if balance < 0:
            debtors.append([user_id, abs(balance)])
        elif balance > 0:
            creditors.append([user_id, balance])
    
    # Sort by amount (largest first)
    debtors.sort(key=lambda x: x[1], reverse=True)
    creditors.sort(key=lambda x: x[1], reverse=True)
    
    # Generate optimized settlements
    settlements = []
    members = GroupMember.objects.filter(group=group)
    member_dict = {m.user.user_id: m.user for m in members}
    
    i, j = 0, 0
    while i < len(debtors) and j < len(creditors):
        debtor_id = debtors[i][0]
        debt_amount = Decimal(str(debtors[i][1]))  # Convert to Decimal
        
        creditor_id = creditors[j][0]
        credit_amount = Decimal(str(creditors[j][1]))  # Convert to Decimal
        
        # Match smallest of the two
        settlement_amount = min(debt_amount, credit_amount)
        
        # Create settlement record
        settlement = Settlement(
            group=group,
            payer=member_dict[debtor_id],
            payee=member_dict[creditor_id],
            amount=settlement_amount,
            is_completed=False
        )
        settlements.append(settlement)
        
        # Update remaining amounts (use Decimal for proper arithmetic)
        debtors[i][1] = debt_amount - settlement_amount
        creditors[j][1] = credit_amount - settlement_amount
        
        # Move to next if current is settled
        if debtors[i][1] <= 0:
            i += 1
        if creditors[j][1] <= 0:
            j += 1
    
    return settlements


def get_settlement_summary(group, user):
    """
    Get settlement summary for a specific user in a group.
    Returns dict with:
    - owes: list of Balance objects where user owes
    - owed: list of Balance objects where user is owed
    - total_owes: sum of amounts owed
    - total_owed: sum of amounts owed to user
    - net_balance: total_owed - total_owes
    """
    owes = Balance.objects.filter(group=group, user1=user)
    owed = Balance.objects.filter(group=group, user2=user)
    
    total_owes = sum(b.amount for b in owes)
    total_owed = sum(b.amount for b in owed)
    net_balance = total_owed - total_owes
    
    return {
        'owes': owes,
        'owed': owed,
        'total_owes': total_owes,
        'total_owed': total_owed,
        'net_balance': net_balance,
    }


def get_user_balance_summary(user, group=None):
    owes = Balance.objects.filter(user1=user)
    owed = Balance.objects.filter(user2=user)
    
    if group:
        owes = owes.filter(group=group)
        owed = owed.filter(group=group)
    
    total_owes = sum(b.amount for b in owes)
    total_owed = sum(b.amount for b in owed)
    net_balance = total_owed - total_owes
    
    return {
        'owes': owes,
        'owed': owed,
        'total_owes': total_owes,
        'total_owed': total_owed,
        'net_balance': net_balance
    }
