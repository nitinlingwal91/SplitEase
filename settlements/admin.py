from django.contrib import admin
from .models import Balance, Settlement


@admin.register(Balance)
class BalanceAdmin(admin.ModelAdmin):
    list_display = ['user1', 'user2', 'amount', 'group']
    list_filter = ['group',]
    search_fields = ['user1__name', 'user2__name', 'group__name']


@admin.register(Settlement)
class SettlementAdmin(admin.ModelAdmin):
    list_display = ['payer', 'payee', 'amount', 'is_completed', 'created_at']
    list_filter = ['is_completed', 'created_at', 'group']
    search_fields = ['payer__name', 'payee__name']
    readonly_fields = ['created_at', 'completed_at']

