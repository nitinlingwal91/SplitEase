from django import forms
from .models import Expense, Category
from groups.models import GroupMember
from users.models import User


class ExpenseForm(forms.ModelForm):
    participants = forms.ModelMultipleChoiceField(
        queryset=None,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=True,
        help_text="Select all participants who will share this expense"
    )
    
    class Meta:
        model = Expense
        fields = ['amount', 'description', 'date', 'category', 'split_type']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.01',
                'placeholder': 'Enter amount',
                'min': '0.01'
            }),
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Dinner at restaurant'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control', 
                'type': 'date'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'split_type': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        group = kwargs.pop('group', None)
        super().__init__(*args, **kwargs)
        
        # Set category queryset to show all available categories
        self.fields['category'].queryset = Category.objects.all().order_by('name')
        self.fields['category'].empty_label = "-- Select Category --"
        
        # Set participants based on group members
        if group:
            # member_ids = GroupMember.objects.filter(group=group).values_list('user_id', flat=True)
            # self.fields['participants'].queryset = User.objects.filter(user_id__in=member_ids)
            
            members = GroupMember.objects.filter(group=group).select_related('user')
            self.fields['participants'].queryset = members
            
            # Pre-select all members for new expense
            if not self.instance.pk:
                self.fields['participants'].initial = members
