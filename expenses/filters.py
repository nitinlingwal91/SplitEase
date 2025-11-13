import django_filters
from .models import Expense
from django import forms

class ExpenseFilter(django_filters.FilterSet):
    date_from = django_filters.DateFilter(
        field_name='date',
        lookup_expr='gte',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    date_to = django_filters.DateFilter(
        field_name='date',
        lookup_expr='lte',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    category = django_filters.CharFilter(
        field_name='category__name',
        lookup_expr='icontains',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search category'})
    )
    payer = django_filters.CharFilter(
        field_name='payer__name',
        lookup_expr='icontains',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search payer'})
    )
    description = django_filters.CharFilter(
        lookup_expr='icontains',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search description'})
    )
    amount_min = django_filters.NumberFilter(
        field_name='amount',
        lookup_expr='gte',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Min amount'})
    )
    amount_max = django_filters.NumberFilter(
        field_name='amount',
        lookup_expr='lte',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Max amount'})
    )

    class Meta:
        model = Expense
        fields = []
