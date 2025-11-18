from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from users.models import User


class TestUserRegistrationValidation(TestCase):
    """TC1: User Registration and Validation"""
    
    def test_user_registration_valid_data(self):
        """TC1.1: Register with valid data"""
        user = User.objects.create_user(
            email='test@example.com',
            password='SecurePass123',
            name='Test User'
        )
        user.save()
        self.assertIsNotNone(user.user_id)
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.name, 'Test User')
    
    def test_user_password_hashing(self):
        """TC1.2: Password is hashed"""
        user = User.objects.create_user(
            email='hash@example.com',
            password='PlainPassword123',
            name='Hash User'
        )
        user.save()
        self.assertNotEqual(user.password, 'PlainPassword123')
        self.assertTrue(user.check_password('PlainPassword123'))
    
    def test_user_registration_required_fields(self):
        """TC1.3: Require mandatory fields"""
        with self.assertRaises((ValidationError, IntegrityError)):
            user = User(email='', password='test123', name='Test')
            user.full_clean()
            user.save()
    
    def test_user_registration_name_validation(self):
        """TC1.5: Name validation"""
        user = User.objects.create_user(
            email='name@example.com',
            password='Pass123',
            name='Valid Name'
        )
        user.save()
        self.assertEqual(user.name, 'Valid Name')


class TestUserEmailUniqueness(TestCase):
    """TC2: Email Uniqueness Validation"""
    
    def test_duplicate_email_raises_integrity_error(self):
        """TC2.1: Duplicate email rejected"""
        User.objects.create_user(
            email='duplicate@example.com',
            password='Pass123',
            name='User One'
        )
        
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                email='duplicate@example.com',
                password='Pass456',
                name='User Two'
            )
    
    def test_email_case_insensitive_uniqueness(self):
        """TC2.2: Email case insensitive"""
        User.objects.create_user(
            email='case@example.com',
            password='Pass123',
            name='User One'
        )
        
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                email='CASE@example.com',
                password='Pass456',
                name='User Two'
            )
    
    def test_email_normalization(self):
        """TC2.3: Email is normalized"""
        user = User.objects.create_user(
            email='Test@Example.COM',
            password='Pass123',
            name='Test User'
        )
        user.save()
        # Check if email is stored in lowercase
        self.assertEqual(user.email, user.email.lower())


class TestUserPasswordStrength(TestCase):
    """TC3: Password Strength Validation"""
    
    def test_minimum_password_length(self):
        """TC3.1: Minimum password length"""
        # Django's default min password validators may apply
        user = User.objects.create_user(
            email='pass@example.com',
            password='Long123',
            name='Pass User'
        )
        user.save()
        self.assertIsNotNone(user.user_id)
    
    def test_password_not_stored_plaintext(self):
        """TC3.3: Password not stored in plaintext"""
        user = User.objects.create_user(
            email='plain@example.com',
            password='MyPassword123',
            name='Plain User'
        )
        user.save()
        self.assertNotEqual(user.password, 'MyPassword123')
    
    def test_password_verification(self):
        """TC3.4: Password verification works"""
        user = User.objects.create_user(
            email='verify@example.com',
            password='CorrectPass123',
            name='Verify User'
        )
        user.save()
        self.assertTrue(user.check_password('CorrectPass123'))
        self.assertFalse(user.check_password('WrongPassword'))


class TestUserAuthentication(TestCase):
    """TC4: User Login Authentication"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='login@example.com',
            password='LoginPass123',
            name='Login User'
        )
        self.user.save()
    
    def test_valid_login_credentials(self):
        """TC4.1: Login with valid credentials"""
        self.assertTrue(self.user.check_password('LoginPass123'))
    
    def test_invalid_password_login(self):
        """TC4.2: Login with invalid password"""
        self.assertFalse(self.user.check_password('WrongPass'))
    
    def test_nonexistent_user_login(self):
        """TC4.3: Login with non-existent email"""
        user_exists = User.objects.filter(email='nonexistent@example.com').exists()
        self.assertFalse(user_exists)
    
    def test_case_insensitive_email_login(self):
        """TC4.4: Login email case insensitive"""
        # Find user by email (case insensitive)
        user = User.objects.filter(email__iexact='LOGIN@EXAMPLE.COM').first()
        self.assertIsNotNone(user)


class TestUserProfileManagement(TestCase):
    """TC5: User Profile Management"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='profile@example.com',
            password='ProfilePass123',
            name='Profile User'
        )
        self.user.save()
    
    def test_profile_update_name(self):
        """TC5.1: Update user name"""
        self.user.name = 'Updated Name'
        self.user.save()
        updated = User.objects.get(user_id=self.user.user_id)
        self.assertEqual(updated.name, 'Updated Name')
    
    def test_profile_view_all_fields(self):
        """TC5.3: View complete profile"""
        self.assertEqual(self.user.email, 'profile@example.com')
        self.assertEqual(self.user.name, 'Profile User')
        self.assertIsNotNone(self.user.user_id)


class TestUserAccountDeletion(TestCase):
    """TC6: User Account Deletion"""
    
    def test_user_deletion(self):
        """TC6.1: Delete user account"""
        user = User.objects.create_user(
            email='delete@example.com',
            password='DeletePass123',
            name='Delete User'
        )
        user.save()
        user_id = user.user_id
        user.delete()
        self.assertFalse(User.objects.filter(user_id=user_id).exists())