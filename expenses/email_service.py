from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string


def send_expense_notification(expense):
    """Send email notification when a new expense is added"""
    subject = f'New Expense: {expense.description}'
    group_members = expense.group.members.all()
    recipient_list = [member.user.email for member in group_members if member.user != expense.payer]
    
    if not recipient_list:
        return
    
    context = {
        'expense': expense,
        'payer': expense.payer.name,
        'group': expense.group.name,
    }
    
    html_message = f"""
    <h3>New Expense Added</h3>
    <p>Hi,</p>
    <p><strong>{expense.payer.name}</strong> added a new expense to <strong>{expense.group.name}</strong></p>
    <p>
        <strong>Description:</strong> {expense.description}<br>
        <strong>Amount:</strong> {expense.amount} {expense.group.currency}<br>
        <strong>Date:</strong> {expense.date}<br>
        <strong>Category:</strong> {expense.category.name if expense.category else 'Uncategorized'}
    </p>
    <p>Log in to SplitEase to view the details and your share.</p>
    """
    
    send_mail(
        subject,
        f'New expense added: {expense.description}',
        settings.DEFAULT_FROM_EMAIL,
        recipient_list,
        html_message=html_message,
        fail_silently=True,
    )


def send_settlement_reminder(settlement):
    """Send payment reminder"""
    subject = f'Payment Reminder: {settlement.amount} {settlement.group.currency} due'
    
    html_message = f"""
    <h3>Settlement Reminder</h3>
    <p>Hi {settlement.payee.name},</p>
    <p><strong>{settlement.payer.name}</strong> owes you <strong>{settlement.amount} {settlement.group.currency}</strong></p>
    <p>Please mark this as settled once you receive the payment.</p>
    """
    
    send_mail(
        subject,
        f'Settlement reminder for {settlement.group.name}',
        settings.DEFAULT_FROM_EMAIL,
        [settlement.payee.email],
        html_message=html_message,
        fail_silently=True,
    )
