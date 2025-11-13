from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout as auth_logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count
from django.utils.timezone import now
from datetime import timedelta
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm, PasswordChangeForm
from .models import User, UserPreference
from groups.models import Group
from expenses.models import Expense
from activities.models import Activity
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from chat.models import UserActivity
import json


def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, 'Registration successful! Please login.')
            return redirect('users:login')
    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form})


def send_verification_email(user, request):
    """Send email verification link to user"""
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    
    verification_link = request.build_absolute_uri(
        f'/users/verify-email/{uid}/{token}/'
    )
    
    subject = 'Verify Your SplitEase Account'
    message = f"""
    Hi {user.name},
    
    Welcome to SplitEase! Please verify your email address by clicking the link below:
    
    {verification_link}
    
    This link will expire in 24 hours.
    
    If you didn't create an account, please ignore this email.
    
    Best regards,
    SplitEase Team
    """
    
    html_message = f"""
    <h3>Hi {user.name},</h3>
    <p>Welcome to <strong>SplitEase</strong>!</p>
    <p>Please verify your email address by clicking the button below:</p>
    <p><a href="{verification_link}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">Verify Email</a></p>
    <p>This link will expire in 24 hours.</p>
    <p>If you didn't create an account, please ignore this email.</p>
    <p>Best regards,<br>SplitEase Team</p>
    """
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_message,
        fail_silently=False,
    )


@login_required
def resend_verification_email(request):
    """Resend verification email"""
    if request.user.email_verified:
        messages.info(request, 'Your email is already verified.')
        return redirect('dashboard')
    
    send_verification_email(request.user, request)
    messages.success(request, 'Verification email sent! Please check your inbox.')
    return redirect('dashboard')


def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.name}!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid email or password.')
    else:
        form = UserLoginForm()
    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    """Logout user and mark as offline in all groups"""
    
    # Mark user as offline in all groups
    UserActivity.objects.filter(user=request.user).update(
        is_online=False
    )
    
    # Logout
    auth_logout(request)
    
    messages.success(request, 'You have been logged out successfully.')
    return redirect('users:login')


@login_required
def profile_view(request):
    """Display user profile with statistics"""
    user = request.user
    
    # Get statistics
    from groups.models import GroupMember
    from expenses.models import Expense
    
    total_groups = GroupMember.objects.filter(user=user).count()
    total_expenses = Expense.objects.filter(payer=user).count()
    total_shared = Expense.objects.filter(payer=user).aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    # Get age
    age = user.get_age()
    
    context = {
        'user': user,
        'total_groups': total_groups,
        'total_expenses': total_expenses,
        'total_shared': total_shared,
        'age': age,
    }
    return render(request, 'users/profile.html', context)


@login_required
def profile_update_view(request):
    """Update user profile information"""
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, '✓ Profile updated successfully!')
            return redirect('users:profile')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = UserProfileForm(instance=request.user)
    
    context = {
        'form': form,
        'form_title': 'Edit Profile',
    }
    return render(request, 'users/profile_form.html', context)


@login_required
def change_password_view(request):
    """Change user password"""
    
    if request.method == 'POST':
        form = PasswordChangeForm(request.POST, user=request.user)
        if form.is_valid():
            user = request.user
            user.set_password(form.cleaned_data['new_password'])
            user.save()
            
            # Update session to avoid logout
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, user)
            
            messages.success(request, '✓ Password changed successfully!')
            return redirect('users:profile')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{error}')
    else:
        form = PasswordChangeForm(user=request.user)
    
    context = {
        'form': form,
        'form_title': 'Change Password',
    }
    return render(request, 'users/password_form.html', context)


@login_required
def delete_account_view(request):
    """Delete user account"""
    
    if request.method == 'POST':
        user = request.user
        email = user.email
        
        # Logout first
        from django.contrib.auth import logout
        logout(request)
        
        # Delete user
        user.delete()
        
        messages.success(request, f'Account {email} has been deleted.')
        return redirect('users:login')
    
    return render(request, 'users/delete_account.html')


@login_required
def dashboard_view(request):
    user = request.user
    groups = user.group_memberships.all().select_related('group')[:5]

    # Get all group IDs for the user
    group_ids = [membership.group.group_id for membership in user.group_memberships.all()]
    
    # 1. EXPENSE BREAKDOWN BY CATEGORY (Pie Chart)
    category_data = Expense.objects.filter(group__group_id__in=group_ids) \
                    .values('category__name') \
                    .annotate(total=Sum('amount')) \
                    .order_by('-total')[:10]
    
    categories = [item['category__name'] or 'Uncategorized' for item in category_data]
    category_amounts = [float(item['total']) for item in category_data]
    
    # 2. SPENDING TRENDS (Line Chart) - Last 6 months
    today = now().date()
    months = []
    spending = []
    
    for i in range(5, -1, -1):
        # Calculate month start and end
        if i == 0:
            month_start = today.replace(day=1)
        else:
            month_start = (today.replace(day=1) - timedelta(days=30*i)).replace(day=1)
        
        month_end = (month_start.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        month_label = month_start.strftime('%b %Y')
        
        total_spent = Expense.objects.filter(
            group__group_id__in=group_ids,
            date__range=[month_start, month_end]
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        months.append(month_label)
        spending.append(float(total_spent))
    
    # 3. TOP SPENDERS (Bar Chart)
    top_spenders = Expense.objects.filter(group__group_id__in=group_ids) \
                    .values('payer__name') \
                    .annotate(total=Sum('amount')) \
                    .order_by('-total')[:5]
    
    spender_names = [item['payer__name'] for item in top_spenders]
    spender_amounts = [float(item['total']) for item in top_spenders]
    
    # 4. SUMMARY STATISTICS
    total_expenses = Expense.objects.filter(group__group_id__in=group_ids).aggregate(Sum('amount'))['amount__sum'] or 0
    total_groups = len(group_ids)
    total_members = sum([g.group.get_total_members() for g in groups])
    
    context = {
        'user': user,
        'groups': groups,
        # Pie Chart Data
        'categories': json.dumps(categories),
        'category_amounts': json.dumps(category_amounts),
        # Line Chart Data
        'months': json.dumps(months),
        'spending': json.dumps(spending),
        # Bar Chart Data
        'spender_names': json.dumps(spender_names),
        'spender_amounts': json.dumps(spender_amounts),
        # Summary Stats
        'total_expenses': total_expenses,
        'total_groups': total_groups,
        'total_members': total_members,
    }
    return render(request, 'dashboard.html', context)

@login_required
def toggle_dark_mode(request):
    """Toggle dark mode preference"""
    if request.method == 'POST':
        preference, created = UserPreference.objects.get_or_create(user=request.user)
        preference.dark_mode = not preference.dark_mode
        preference.save()
        messages.success(request, 'Theme preference updated!')
    
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))
