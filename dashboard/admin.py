from django.contrib import admin
from .models import (Income, ExpenseRequest, Retirement, Announcement,
                     Comment, UserProfile, DefaultDateRange, NetBalance)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'department', 'phone', 'created_at']
    list_filter = ['role', 'department']
    search_fields = ['user__username', 'user__email']


@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ['source', 'amount', 'date']
    list_filter = ['source', 'date']
    fields = ['source', 'source_name', 'amount', 'date']
    search_fields = ['source_name', 'description']
    date_hierarchy = 'date'


@admin.register(ExpenseRequest)
class ExpenseRequestAdmin(admin.ModelAdmin):
    list_display = ['department', 'category', 'amount', 'status', 'date', 'requested_by']
    list_filter = ['status', 'department', 'date']
    search_fields = ['category', 'description']
    date_hierarchy = 'date'


@admin.register(Retirement)
class RetirementAdmin(admin.ModelAdmin):
    list_display = ['department', 'category', 'amount', 'status', 'date', 'submitted_by']
    list_filter = ['status', 'department', 'date']
    search_fields = ['category', 'description']
    date_hierarchy = 'date'
    fields = ['department', 'category', 'amount', 'date', 'status', 'description']


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'created_by', 'created_at']
    list_filter = ['is_active']
    search_fields = ['title', 'content']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'is_approved', 'created_at']
    list_filter = ['is_approved']
    search_fields = ['name', 'email', 'message']


@admin.register(DefaultDateRange)
class DefaultDateRangeAdmin(admin.ModelAdmin):
    list_display = ['name', 'days_back', 'is_active', 'updated_at']


@admin.register(NetBalance)
class NetBalanceAdmin(admin.ModelAdmin):
    list_display = ['amount', 'updated_by', 'updated_at']
    readonly_fields = ['updated_at']
