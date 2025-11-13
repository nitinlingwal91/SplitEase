from django.db import models
from django.utils import timezone
from users.models import User
from groups.models import Group


class Balance(models.Model):
    balance_id = models.AutoField(primary_key=True)
    user1 = models.ForeignKey(User, related_name='balance_from', on_delete=models.CASCADE)
    user2 = models.ForeignKey(User, related_name='balance_to', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'balances'
        unique_together = ['user1', 'user2', 'group']

    def __str__(self):
        return f"{self.user1.name} owes {self.user2.name}: {self.amount}"


class Settlement(models.Model):
    settlement_id = models.AutoField(primary_key=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='settlements')
    payer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments_made')
    payee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments_received')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_completed = models.BooleanField(default=False)  # ADD THIS LINE
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)  # OPTIONAL: Add this too
    
    class Meta:
        db_table = 'settlements_settlement'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.payer.name} → {self.payee.name}: {self.amount}"

