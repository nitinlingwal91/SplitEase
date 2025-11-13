from django.contrib import admin
from .models import Category, Expense, ExpenseParticipant


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']


class ExpenseParticipantInline(admin.TabularInline):
    model = ExpenseParticipant
    extra = 1


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['description', 'amount', 'payer', 'group', 'date', 'category']
    list_filter = ['split_type', 'category', 'date']
    search_fields = ['description', 'payer__name']
    inlines = [ExpenseParticipantInline]
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ExpenseParticipant)
class ExpenseParticipantAdmin(admin.ModelAdmin):
    list_display = ['expense', 'user', 'share_amount', 'is_settled']
    list_filter = ['is_settled']

