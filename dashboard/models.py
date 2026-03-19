from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


DEPARTMENT_CHOICES = [
    ('OfisiMchungaji', 'Ofisi Ya Mchungaji'),
    ('fedha', 'Finance'),
    ('elimu', 'Education'),
    ('afya', 'Afya'),
    ('huduma', 'Huduma Binafsi'),
    ('vijana', 'Vijana'),
    ('wanawake', "Wana wa kike"),
    ('uwakili', 'Uwakili'),
    ('majengo', 'Majengo'),
    ('mawasiliano', 'Mawasiliano'),
    ('atape', 'Atape'),
    ('ss', 'SS'),
    ('newstart', 'New Start'),
    ('familia', 'Huduma za Familia'),
    ('vbs', 'VBS'),
    ('muziki', 'Muziki'),
    ('maombi', "Maombi"),
    ('vop', 'VOP'),
    ('fedha', 'Fedha'),
    ('watoto', 'Watoto'),
    ('uchapaji', 'Uchapaji'),
    ('mahitaji', 'Mahitaji Maalumu'),
    ('amo&dorcas', "AMO & Dorcas"),
    ('kwaya', 'Kwaya ya Kanisa'),
    ('syc', 'SYC'),
    ('shadow', ' Shadow of Calvary'),
    ('mashemasi', 'Mashemasi'),
    ('nyingineyo', 'Nyingineyo'),
]

STATUS_CHOICES_EXPENSE = [
    ('pending', 'Pending'),
    ('approved', 'Approved'),
    ('not_approved', 'Not Approved'),
]

STATUS_CHOICES_RETIREMENT = [
    ('open', 'Open'),
    ('closed', 'Closed'),
]

INCOME_SOURCE_CHOICES = [
    ('zaka', 'Zaka'),
    ('sadaka', 'Sadaka'),
    ('mk', 'MK'),
    ('other', 'Other'),
]


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('user', 'User'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"

    def is_admin(self):
        return self.role == 'admin'


class Announcement(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Comment(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.created_at.strftime('%Y-%m-%d')}"


class Income(models.Model):
    source = models.CharField(max_length=20, choices=INCOME_SOURCE_CHOICES, default='other')
    source_name = models.CharField(max_length=200, blank=True, help_text="Custom source name for 'Other' income")
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    date = models.DateField(default=timezone.now)
    description = models.TextField(blank=True)
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='incomes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.get_source_display()} - TSH {self.amount:,.2f} ({self.date})"

    def get_display_name(self):
        if self.source_name:
            return self.source_name
        return self.get_source_display()


class ExpenseRequest(models.Model):
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES)
    category = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES_EXPENSE, default='pending')
    requested_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='expense_requests')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_expenses')
    date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    review_notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.get_department_display()} - {self.category} - TSH {self.amount:,.2f}"


class Retirement(models.Model):
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES)
    category = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES_RETIREMENT, default='open')
    submitted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='retirements')
    date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.get_department_display()} - {self.category} - TSH {self.amount:,.2f}"


class DefaultDateRange(models.Model):
    """Admin-configurable default date range shown on dashboard."""
    name = models.CharField(max_length=100, default='Default Range')
    days_back = models.IntegerField(default=14, help_text='Number of days back from today (e.g., 7 for last 7 days)')
    is_active = models.BooleanField(default=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.name} (last {self.days_back} days)"


class NetBalance(models.Model):
    """Manual net balance value set by admin."""

    amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"Net Balance: TSH {self.amount:,.2f} (updated {self.updated_at:%Y-%m-%d %H:%M})"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Automatically create a UserProfile for every new user."""
    if created:
        UserProfile.objects.create(user=instance, role='admin' if instance.is_superuser else 'user')
