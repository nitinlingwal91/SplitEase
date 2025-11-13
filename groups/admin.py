from django.contrib import admin
from .models import Group, GroupMember


class GroupMemberInline(admin.TabularInline):
    model = GroupMember
    extra = 1


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'currency', 'created_at']
    list_filter = ['currency', 'created_at']
    search_fields = ['name', 'owner__name']
    inlines = [GroupMemberInline]


@admin.register(GroupMember)
class GroupMemberAdmin(admin.ModelAdmin):
    list_display = ['user', 'group', 'joined_date', 'is_admin']
    list_filter = ['is_admin', 'joined_date']
    search_fields = ['user__name', 'group__name']

