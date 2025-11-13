from django import forms
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
from .models import User
import re



class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter password'}),
        min_length=8,
        help_text='Password must be at least 8 characters long.'
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm password'}),
        label='Confirm Password'
    )
    
    class Meta:
        model = User
        fields = ['name', 'email',]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your full name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email address'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+91 1234567890 (optional)'
            }),
        }
    
    def clean_email(self):
        """Validate email format and uniqueness"""
        email = self.cleaned_data.get('email', '').strip().lower()
        
        # Validate email format
        email_validator = EmailValidator(message='Enter a valid email address.')
        try:
            email_validator(email)
        except ValidationError:
            raise ValidationError('Invalid email format.')
        
        # Check for common disposable email domains
        disposable_domains = ['tempmail.com', 'guerrillamail.com', 'mailinator.com', '10minutemail.com']
        domain = email.split('@') if '@' in email else ''
        if domain in disposable_domains:
            raise ValidationError('Disposable email addresses are not allowed.')
        
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            raise ValidationError('An account with this email already exists.')
        
        return email
    
    def clean_phone_number(self):
        """Validate phone number format"""
        phone = self.cleaned_data.get('phone_number', '').strip()
        
        if phone:
            # Remove spaces and special characters
            phone_clean = re.sub(r'[^\d+]', '', phone)
            
            # Validate format (basic international format)
            if not re.match(r'^\+?\d{10,15}$', phone_clean):
                raise ValidationError('Enter a valid phone number (10-15 digits).')
            
            return phone_clean
        
        return phone
    
    def clean(self):
        """Validate password match"""
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password:
            if password != confirm_password:
                raise ValidationError('Passwords do not match.')
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = user.email.lower()  # Store email in lowercase
        user.set_password(self.cleaned_data['password'])
        
        if commit:
            user.save()
        
        return user
    
    
class AddMemberForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'member@example.com'
        }),
        help_text='Enter the email address of the user to add.'
    )
    
    def clean_email(self):
        """Validate email format"""
        email = self.cleaned_data.get('email', '').strip().lower()
        
        # Validate email format
        email_validator = EmailValidator(message='Enter a valid email address.')
        try:
            email_validator(email)
        except ValidationError:
            raise ValidationError('Invalid email format.')
        
        # Check if user exists
        if not User.objects.filter(email=email).exists():
            raise ValidationError('No user found with this email address.')
        
        return email


class UserLoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control', 'placeholder': 'Email'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'Password'
    }))


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'email', 'phone_number', 'date_of_birth', 'bio', 'profile_picture']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your full name',
                'maxlength': '100'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email',
                'readonly': 'readonly'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+91 1234567890',
                'maxlength': '20'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Tell us about yourself...',
                'rows': 3,
                'maxlength': '500'
            }),
            'profile_picture': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }
    
    def clean_phone_number(self):
        """Validate phone number"""
        phone = self.cleaned_data.get('phone_number')
        
        if phone is None:
        # Field is empty or missing
            return ''
        phone = phone.strip()
        # Your existing validation logic:
        phone_clean = re.sub(r'[^\d+]', '', phone)
        if not re.match(r'^\+?\d{10,15}$', phone_clean):
            raise ValidationError('Enter a valid phone number (10-15 digits).')
        return phone_clean
    
    def clean_date_of_birth(self):
        """Validate date of birth"""
        dob = self.cleaned_data.get('date_of_birth')
        
        if dob:
            from django.utils import timezone
            today = timezone.now().date()
            
            if dob > today:
                raise ValidationError('Date of birth cannot be in the future.')
            
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            
            if age < 13:
                raise ValidationError('You must be at least 13 years old.')
            
            if age > 120:
                raise ValidationError('Please enter a valid date of birth.')
        
        return dob
    
    def clean_bio(self):
        """Clean bio text"""
        bio = self.cleaned_data.get('bio', '').strip()
        
        if len(bio) > 500:
            raise ValidationError('Bio cannot exceed 500 characters.')
        
        return bio


class PasswordChangeForm(forms.Form):
    """Custom password change form with better validation"""
    
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your current password'
        }),
        label='Current Password'
    )
    
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter new password (min 8 characters)',
            'minlength': '8'
        }),
        label='New Password',
        min_length=8,
        help_text='Must be at least 8 characters long'
    )
    
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm new password'
        }),
        label='Confirm New Password'
    )
    
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
    
    def clean(self):
        cleaned_data = super().clean()
        current_password = cleaned_data.get('current_password')
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        
        # Verify current password
        if current_password and self.user:
            if not self.user.check_password(current_password):
                raise ValidationError('Current password is incorrect.')
        
        # Check new passwords match
        if new_password and confirm_password:
            if new_password != confirm_password:
                raise ValidationError('New passwords do not match.')
        
        # Check password is different from current
        if current_password and new_password:
            if current_password == new_password:
                raise ValidationError('New password must be different from current password.')
        
        return cleaned_data
        

