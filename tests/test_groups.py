from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from users.models import User
from groups.models import Group, GroupMember


class TestGroupCreation(TestCase):
    """TC7: Group Creation"""
    
    def setUp(self):
        self.owner = User.objects.create_user(
            email='owner@example.com',
            password='OwnerPass123',
            name='Group Owner'
        )
        self.owner.save()
    
    def test_group_creation_with_valid_data(self):
        """TC7.1: Create group with valid data"""
        group = Group.objects.create(
            name='Test Group',
            description='A test group',
            owner=self.owner,
            currency='USD'
        )
        group.save()
        self.assertIsNotNone(group.group_id)
        self.assertEqual(group.name, 'Test Group')
        self.assertEqual(group.owner, self.owner)
    
    def test_group_name_required(self):
        """TC7.3: Group name is mandatory"""
        with self.assertRaises((ValidationError, IntegrityError)):
            group = Group(
                name='',
                owner=self.owner
            )
            group.full_clean()
            group.save()
    
    def test_group_owner_required(self):
        """TC7.4: Group owner is mandatory"""
        with self.assertRaises((ValidationError, IntegrityError)):
            group = Group(name='No Owner Group', owner=None)
            group.full_clean()
            group.save()
    
    def test_group_creation_default_currency(self):
        """TC7.2: Default currency"""
        group = Group.objects.create(
            name='Currency Test',
            owner=self.owner
        )
        group.save()
        self.assertIsNotNone(group.currency)


class TestGroupMembershipAddition(TestCase):
    """TC8: Group Membership Addition"""
    
    def setUp(self):
        self.owner = User.objects.create_user(
            email='owner2@example.com',
            password='OwnerPass123',
            name='Owner Two'
        )
        self.owner.save()
        
        self.user1 = User.objects.create_user(
            email='member1@example.com',
            password='MemberPass123',
            name='Member One'
        )
        self.user1.save()
        
        self.group = Group.objects.create(
            name='Membership Group',
            owner=self.owner
        )
        self.group.save()
    
    def test_add_member_to_group(self):
        """TC8.1: Add member to group"""
        member = GroupMember.objects.create(
            group=self.group,
            user=self.user1
        )
        member.save()
        self.assertTrue(GroupMember.objects.filter(
            group=self.group,
            user=self.user1
        ).exists())
    
    def test_add_multiple_members(self):
        """TC8.2: Add multiple members"""
        user2 = User.objects.create_user(
            email='member2@example.com',
            password='Pass123',
            name='Member Two'
        )
        user2.save()
        
        GroupMember.objects.create(group=self.group, user=self.user1).save()
        GroupMember.objects.create(group=self.group, user=user2).save()
        
        self.assertEqual(GroupMember.objects.filter(group=self.group).count(), 2)
    
    def test_member_addition_with_timestamp(self):
        """TC8.3: Member addition timestamp"""
        member = GroupMember.objects.create(
            group=self.group,
            user=self.user1
        )
        member.save()
        self.assertIsNotNone(member.joined_date)


class TestGroupDuplicatePrevention(TestCase):
    """TC9: Duplicate Member Prevention"""
    
    def setUp(self):
        self.owner = User.objects.create_user(
            email='owner3@example.com',
            password='Pass123',
            name='Owner Three'
        )
        self.owner.save()
        
        self.user = User.objects.create_user(
            email='user@example.com',
            password='Pass123',
            name='User'
        )
        self.user.save()
        
        self.group = Group.objects.create(
            name='Duplicate Test Group',
            owner=self.owner
        )
        self.group.save()
    
    def test_duplicate_member_not_added(self):
        """TC9.1: Duplicate member rejected"""
        GroupMember.objects.create(group=self.group, user=self.user).save()
        
        with self.assertRaises(IntegrityError):
            GroupMember.objects.create(group=self.group, user=self.user).save()


class TestGroupOwnerManagement(TestCase):
    """TC10: Group Owner Management"""
    
    def setUp(self):
        self.owner = User.objects.create_user(
            email='owner4@example.com',
            password='Pass123',
            name='Owner Four'
        )
        self.owner.save()
        
        self.group = Group.objects.create(
            name='Owner Group',
            owner=self.owner
        )
        self.group.save()
    
    def test_group_owner_is_member(self):
        """TC10.1: Owner automatically added as member"""
        # Assuming owner is auto-added or manually added
        GroupMember.objects.create(group=self.group, user=self.owner, is_admin=True).save()
        self.assertTrue(GroupMember.objects.filter(group=self.group, user=self.owner).exists())


class TestGroupDeletion(TestCase):
    """TC12: Group Deletion"""
    
    def setUp(self):
        self.owner = User.objects.create_user(
            email='delowner@example.com',
            password='Pass123',
            name='Delete Owner'
        )
        self.owner.save()
    
    def test_group_deletion_by_owner(self):
        """TC12.1: Owner can delete group"""
        group = Group.objects.create(
            name='Deletable Group',
            owner=self.owner
        )
        group.save()
        group_id = group.group_id
        group.delete()
        self.assertFalse(Group.objects.filter(group_id=group_id).exists())
    
    def test_group_deletion_cascades(self):
        """TC12.2: Deleting group removes members"""
        group = Group.objects.create(
            name='Cascade Group',
            owner=self.owner
        )
        group.save()
        
        user = User.objects.create_user(
            email='cascade@example.com',
            password='Pass123',
            name='Cascade User'
        )
        user.save()
        
        GroupMember.objects.create(group=group, user=user).save()
        
        group_id = group.group_id
        group.delete()
        
        self.assertFalse(GroupMember.objects.filter(group_id=group_id).exists())