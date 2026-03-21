from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum, Q, Case, When, Value, IntegerField
from django.utils import timezone
from datetime import timedelta, date
import json

from .models import (Income, ExpenseRequest, Retirement, Announcement,
                     Comment, UserProfile, DefaultDateRange, NetBalance)
from .forms import (LoginForm, RegisterForm, IncomeForm, ExpenseRequestForm,
                    ExpenseStatusForm, RetirementForm, AnnouncementForm,
                    CommentForm, DateRangeForm, DefaultDateRangeForm, UserProfileForm,
                    NetBalanceForm)


def format_tsh(value):
    if value is None:
        return "TSH 0.00"
    try:
        return f"TSH {float(value):,.2f}"
    except (ValueError, TypeError):
        return "TSH 0.00"


def get_default_date_range():
    try:
        default_range = DefaultDateRange.objects.filter(is_active=True).first()
        if default_range and default_range.from_date and default_range.to_date:
            return default_range.from_date, default_range.to_date
        days = default_range.days_back if default_range else 14
    except Exception:
        days = 14
    today = date.today()
    return today - timedelta(days=days), today


def _parse_date(date_str):
    from datetime import datetime
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except Exception:
        return None


def get_active_filters(request, key='default', include_status=False):
    """Get active date range + department + optional status filter for a view.

    This will:
    - Respect GET params when provided.
    - Store selected filters in session so they persist across requests.
    - Clear stored filters when `reset=1` is in the querystring.

    Returns: (date_from, date_to, department, status, did_reset)
    """
    reset = request.GET.get('reset')
    date_from_str = request.GET.get('date_from', '')
    date_to_str = request.GET.get('date_to', '')
    department = request.GET.get('department', '')
    status = request.GET.get('status', '') if include_status else ''

    if reset:
        request.session.pop(f'{key}_date_from', None)
        request.session.pop(f'{key}_date_to', None)
        request.session.pop(f'{key}_department', None)
        if include_status:
            request.session.pop(f'{key}_status', None)

    if 'date_from' in request.GET:
        if date_from_str:
            request.session[f'{key}_date_from'] = date_from_str
        else:
            request.session.pop(f'{key}_date_from', None)
    if 'date_to' in request.GET:
        if date_to_str:
            request.session[f'{key}_date_to'] = date_to_str
        else:
            request.session.pop(f'{key}_date_to', None)
    if 'department' in request.GET:
        if department:
            request.session[f'{key}_department'] = department
        else:
            request.session.pop(f'{key}_department', None)
    if include_status and 'status' in request.GET:
        if status:
            request.session[f'{key}_status'] = status
        else:
            request.session.pop(f'{key}_status', None)

    stored_from = request.session.get(f'{key}_date_from')
    stored_to = request.session.get(f'{key}_date_to')
    stored_department = request.session.get(f'{key}_department', '')
    stored_status = request.session.get(f'{key}_status', '') if include_status else ''

    date_from = _parse_date(stored_from) if stored_from else None
    date_to = _parse_date(stored_to) if stored_to else None

    return date_from, date_to, stored_department, stored_status, bool(reset)


def is_admin(user):
    if not user.is_authenticated:
        return False
    try:
        return user.profile.is_admin() or user.is_superuser
    except Exception:
        return user.is_superuser


def is_user_or_admin(user):
    return user.is_authenticated


# ============================================================
# Authentication Views
# ============================================================

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
            return redirect(request.GET.get('next', '/'))
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('home')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.save()
            UserProfile.objects.create(
                user=user, role='user',
                department=form.cleaned_data.get('department', ''),
                phone=form.cleaned_data.get('phone', '')
            )
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})


# ============================================================
# Home Dashboard
# ============================================================

def home_view(request):
    default_from, default_to = get_default_date_range()
    date_from, date_to, department, _, _ = get_active_filters(request, key='home')
    if not date_from:
        date_from = default_from
    if not date_to:
        date_to = default_to

    income_qs = Income.objects.filter(date__gte=date_from, date__lte=date_to)
    expense_qs = ExpenseRequest.objects.filter(date__gte=date_from, date__lte=date_to)
    retirement_qs = Retirement.objects.filter(date__gte=date_from, date__lte=date_to)

    # Short lists for home summary tables
    income_shortlist = income_qs.order_by('-date', '-created_at')[:5]
    expense_shortlist = expense_qs.order_by('-date', '-created_at')[:5]
    retirement_shortlist = retirement_qs.order_by('-date', '-created_at')[:5]

    total_income = income_qs.aggregate(total=Sum('amount'))['total'] or 0
    total_expenses = expense_qs.aggregate(total=Sum('amount'))['total'] or 0
    total_retirement = retirement_qs.aggregate(total=Sum('amount'))['total'] or 0

    net_balance_obj = NetBalance.objects.order_by('-updated_at').first()
    net_balance = net_balance_obj.amount if net_balance_obj else 0

    announcements = Announcement.objects.filter(is_active=True)[:5]
    comments = Comment.objects.filter(is_approved=True)[:10]
    comment_form = CommentForm()

    if request.method == 'POST' and 'submit_comment' in request.POST:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment_form.save()
            messages.success(request, 'Your comment has been submitted!')
            return redirect('home')

    context = {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'total_retirement': total_retirement,
        'net_balance': net_balance,
        'announcements': announcements,
        'comments': comments,
        'comment_form': comment_form,
        'date_from': date_from,
        'date_to': date_to,
        'default_from': default_from,
        'default_to': default_to,
        'active_tab': 'home',
        'income_shortlist': income_shortlist,
        'expense_shortlist': expense_shortlist,
        'retirement_shortlist': retirement_shortlist,
    }
    return render(request, 'dashboard/home.html', context)


# ============================================================
# Income Dashboard
# ============================================================

def income_view(request):
    default_from, default_to = get_default_date_range()
    date_from, date_to, department, _, _ = get_active_filters(request, key='income')
    if not date_from:
        date_from = default_from
    if not date_to:
        date_to = default_to

    # source filter support for income dashboard
    source = request.GET.get('source', '')
    if source:
        request.session['income_source'] = source
    elif 'source' in request.GET:
        request.session.pop('income_source', None)
    else:
        source = request.session.get('income_source', '')

    qs = Income.objects.filter(date__gte=date_from, date__lte=date_to)
    if department:
        qs = qs.filter(department=department)
    if source:
        qs = qs.filter(source=source)

    total_zaka = qs.filter(source='zaka').aggregate(total=Sum('amount'))['total'] or 0
    total_sadaka = qs.filter(source='sadaka').aggregate(total=Sum('amount'))['total'] or 0
    total_mk = qs.filter(source='mk').aggregate(total=Sum('amount'))['total'] or 0
    total_other = qs.filter(source='other').aggregate(total=Sum('amount'))['total'] or 0
    total_income = qs.aggregate(total=Sum('amount'))['total'] or 0

    # Order by source priority: zaka -> sadaka -> mk -> other, then newest first
    source_priority = Case(
        When(source='zaka', then=Value(1)),
        When(source='sadaka', then=Value(2)),
        When(source='mk', then=Value(3)),
        default=Value(4),
        output_field=IntegerField(),
    )
    incomes = qs.annotate(source_priority=source_priority).order_by('source_priority', '-date', '-created_at')

    context = {
        'total_zaka': total_zaka,
        'total_sadaka': total_sadaka,
        'total_mk': total_mk,
        'total_other': total_other,
        'total_income': total_income,
        'incomes': incomes,
        'date_from': date_from,
        'date_to': date_to,
        'department': department,
        'source': source,
        'active_tab': 'income',
    }
    return render(request, 'dashboard/income.html', context)


def income_add(request):
    if not is_user_or_admin(request.user):
        messages.error(request, 'Please login to add income.')
        return redirect('login')

    next_url = request.GET.get('next') or request.POST.get('next')

    if request.method == 'POST':
        form = IncomeForm(request.POST)
        if form.is_valid():
            income = form.save(commit=False)
            income.created_by = request.user
            income.save()
            messages.success(request, 'Income record added successfully!')
            return redirect(next_url or 'income')
    else:
        form = IncomeForm()

    return render(request, 'dashboard/income_form.html', {
        'form': form, 'action': 'Add', 'active_tab': 'income',
        'next_url': next_url,
    })


def income_edit(request, pk):
    if not is_user_or_admin(request.user):
        messages.error(request, 'Please login to edit income.')
        return redirect('login')
    income = get_object_or_404(Income, pk=pk)
    next_url = request.GET.get('next') or request.POST.get('next')
    if request.method == 'POST':
        form = IncomeForm(request.POST, instance=income)
        if form.is_valid():
            form.save()
            messages.success(request, 'Income record updated successfully!')
            return redirect(next_url or 'income')
    else:
        form = IncomeForm(instance=income)
    return render(request, 'dashboard/income_form.html', {
        'form': form, 'action': 'Edit', 'income': income, 'active_tab': 'income',
        'next_url': next_url,
    })


def income_detail(request, pk):
    income = get_object_or_404(Income, pk=pk)
    return render(request, 'dashboard/income_detail.html', {'income': income, 'active_tab': 'income'})


def income_delete(request, pk):
    if not is_admin(request.user):
        messages.error(request, 'Only admins can delete records.')
        return redirect('income')
    income = get_object_or_404(Income, pk=pk)
    if request.method == 'POST':
        income.delete()
        messages.success(request, 'Income record deleted.')
    return redirect('income')


# ============================================================
# Expense Request Dashboard
# ============================================================

def expense_view(request):
    default_from, default_to = get_default_date_range()
    date_from, date_to, department, status_filter, _ = get_active_filters(request, key='expenses', include_status=True)
    if not date_from:
        date_from = default_from
    if not date_to:
        date_to = default_to

    qs = ExpenseRequest.objects.filter(date__gte=date_from, date__lte=date_to)
    if department:
        qs = qs.filter(department=department)
    if status_filter:
        qs = qs.filter(status=status_filter)

    base_qs = ExpenseRequest.objects.filter(date__gte=date_from, date__lte=date_to)
    if department:
        base_qs = base_qs.filter(department=department)

    total_requests = base_qs.aggregate(total=Sum('amount'))['total'] or 0
    total_approved = base_qs.filter(status='approved').aggregate(total=Sum('amount'))['total'] or 0
    total_not_approved = base_qs.filter(status='not_approved').aggregate(total=Sum('amount'))['total'] or 0
    total_pending = base_qs.filter(status='pending').aggregate(total=Sum('amount'))['total'] or 0

    context = {
        'expenses': qs,
        'total_requests': total_requests,
        'total_approved': total_approved,
        'total_not_approved': total_not_approved,
        'total_pending': total_pending,
        'count_total': base_qs.count(),
        'count_approved': base_qs.filter(status='approved').count(),
        'count_not_approved': base_qs.filter(status='not_approved').count(),
        'count_pending': base_qs.filter(status='pending').count(),
        'date_from': date_from,
        'date_to': date_to,
        'department': department,
        'status_filter': status_filter,
        'active_tab': 'expenses',
    }
    return render(request, 'dashboard/expenses.html', context)


def expense_add(request):
    if not is_user_or_admin(request.user):
        messages.error(request, 'Please login to add expense request.')
        return redirect('login')

    next_url = request.GET.get('next') or request.POST.get('next')

    if request.method == 'POST':
        form = ExpenseRequestForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.requested_by = request.user
            expense.save()
            messages.success(request, 'Expense request submitted successfully!')
            return redirect(next_url or 'expenses')
    else:
        form = ExpenseRequestForm()
    return render(request, 'dashboard/expense_form.html', {'form': form, 'action': 'Add', 'active_tab': 'expenses', 'next_url': next_url})


def expense_edit(request, pk):
    if not is_user_or_admin(request.user):
        messages.error(request, 'Please login to edit expense request.')
        return redirect('login')
    expense = get_object_or_404(ExpenseRequest, pk=pk)
    next_url = request.GET.get('next') or request.POST.get('next')
    if request.method == 'POST':
        form = ExpenseRequestForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            messages.success(request, 'Expense request updated!')
            return redirect(next_url or 'expenses')
    else:
        form = ExpenseRequestForm(instance=expense)
    return render(request, 'dashboard/expense_form.html', {
        'form': form, 'action': 'Edit', 'expense': expense,
        'active_tab': 'expenses', 'is_admin_user': is_admin(request.user),
        'next_url': next_url,
    })


def expense_status(request, pk):
    if not is_admin(request.user):
        messages.error(request, 'Only admins can change expense status.')
        return redirect('expenses')
    expense = get_object_or_404(ExpenseRequest, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        review_notes = request.POST.get('review_notes', '')
        if new_status in ['pending', 'approved', 'not_approved']:
            expense.status = new_status
            expense.review_notes = review_notes
            expense.reviewed_by = request.user
            expense.save()
            messages.success(request, f'Expense status updated to {expense.get_status_display()}.')
    return redirect('expenses')


def expense_detail(request, pk):
    expense = get_object_or_404(ExpenseRequest, pk=pk)
    return render(request, 'dashboard/expense_detail.html', {'expense': expense, 'active_tab': 'expenses'})


def expense_delete(request, pk):
    if not is_admin(request.user):
        messages.error(request, 'Only admins can delete records.')
        return redirect('expenses')
    expense = get_object_or_404(ExpenseRequest, pk=pk)
    if request.method == 'POST':
        expense.delete()
        messages.success(request, 'Expense request deleted.')
    return redirect('expenses')


# ============================================================
# Retirement Dashboard
# ============================================================

def retirement_view(request):
    default_from, default_to = get_default_date_range()
    date_from, date_to, department, status_filter, _ = get_active_filters(request, key='retirement', include_status=True)
    if not date_from:
        date_from = default_from
    if not date_to:
        date_to = default_to

    qs = Retirement.objects.filter(date__gte=date_from, date__lte=date_to)
    if department:
        qs = qs.filter(department=department)
    if status_filter:
        qs = qs.filter(status=status_filter)

    total_retirement = qs.aggregate(total=Sum('amount'))['total'] or 0
    total_open = qs.filter(status='open').aggregate(total=Sum('amount'))['total'] or 0
    total_closed = qs.filter(status='closed').aggregate(total=Sum('amount'))['total'] or 0

    context = {
        'retirements': qs,
        'total_retirement': total_retirement,
        'total_open': total_open,
        'total_closed': total_closed,
        'date_from': date_from,
        'date_to': date_to,
        'department': department,
        'status_filter': status_filter,
        'active_tab': 'retirement',
    }
    return render(request, 'dashboard/retirement.html', context)


def retirement_add(request):
    if not is_user_or_admin(request.user):
        messages.error(request, 'Please login to add retirement record.')
        return redirect('login')

    next_url = request.GET.get('next') or request.POST.get('next')

    if request.method == 'POST':
        form = RetirementForm(request.POST)
        if form.is_valid():
            retirement = form.save(commit=False)
            retirement.submitted_by = request.user
            retirement.save()
            messages.success(request, 'Retirement record added successfully!')
            return redirect(next_url or 'retirement')
    else:
        form = RetirementForm()
    return render(request, 'dashboard/retirement_form.html', {'form': form, 'action': 'Add', 'active_tab': 'retirement', 'next_url': next_url})


def retirement_edit(request, pk):
    if not is_user_or_admin(request.user):
        messages.error(request, 'Please login to edit retirement record.')
        return redirect('login')
    retirement = get_object_or_404(Retirement, pk=pk)
    next_url = request.GET.get('next') or request.POST.get('next')
    if request.method == 'POST':
        form = RetirementForm(request.POST, instance=retirement)
        if form.is_valid():
            form.save()
            messages.success(request, 'Retirement record updated!')
            return redirect(next_url or 'retirement')
    else:
        form = RetirementForm(instance=retirement)
    return render(request, 'dashboard/retirement_form.html', {
        'form': form, 'action': 'Edit', 'retirement': retirement, 'active_tab': 'retirement',
        'next_url': next_url,
    })


def retirement_detail(request, pk):
    retirement = get_object_or_404(Retirement, pk=pk)
    return render(request, 'dashboard/retirement_detail.html', {'retirement': retirement, 'active_tab': 'retirement'})


def retirement_delete(request, pk):
    if not is_admin(request.user):
        messages.error(request, 'Only admins can delete records.')
        return redirect('retirement')
    retirement = get_object_or_404(Retirement, pk=pk)
    if request.method == 'POST':
        retirement.delete()
        messages.success(request, 'Retirement record deleted.')
    return redirect('retirement')


# ============================================================
# Admin Dashboard
# ============================================================

@login_required
def admin_dashboard(request):
    if not is_admin(request.user):
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')

    default_from, default_to = get_default_date_range()
    date_from, date_to, department, _, _ = get_active_filters(request, key='admin')
    if not date_from:
        date_from = default_from
    if not date_to:
        date_to = default_to

    income_qs = Income.objects.filter(date__gte=date_from, date__lte=date_to)
    expense_qs = ExpenseRequest.objects.filter(date__gte=date_from, date__lte=date_to)
    retirement_qs = Retirement.objects.filter(date__gte=date_from, date__lte=date_to)

    total_income = income_qs.aggregate(total=Sum('amount'))['total'] or 0
    total_expenses = expense_qs.aggregate(total=Sum('amount'))['total'] or 0
    total_retirement = retirement_qs.aggregate(total=Sum('amount'))['total'] or 0
    net_balance_obj = NetBalance.objects.order_by('-updated_at').first()
    net_balance = net_balance_obj.amount if net_balance_obj else 0
    total_users = User.objects.count()
    pending_expenses = ExpenseRequest.objects.filter(status='pending').count()
    active_announcements = Announcement.objects.filter(is_active=True).count()

    recent_income = income_qs.order_by('-date', '-created_at')
    recent_expenses = expense_qs.order_by('-date', '-created_at')
    recent_retirements = retirement_qs.order_by('-date', '-created_at')
    all_users = User.objects.select_related('profile').all()
    announcements = Announcement.objects.all()[:10]
    default_range = DefaultDateRange.objects.filter(is_active=True).first()
    comments = Comment.objects.all()[:10]

    context = {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'total_retirement': total_retirement,
        'net_balance': net_balance,
        'total_users': total_users,
        'pending_expenses': pending_expenses,
        'active_announcements': active_announcements,
        'recent_income': recent_income,
        'recent_expenses': recent_expenses,
        'recent_retirements': recent_retirements,
        'all_users': all_users,
        'announcements': announcements,
        'default_range': default_range,
        'comments': comments,
        'date_from': date_from,
        'date_to': date_to,
        'active_tab': 'admin',
    }
    return render(request, 'dashboard/admin_dashboard.html', context)


@login_required
def admin_announcement_add(request):
    if not is_admin(request.user):
        messages.error(request, 'Access denied.')
        return redirect('home')
    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            ann = form.save(commit=False)
            ann.created_by = request.user
            ann.save()
            messages.success(request, 'Announcement added!')
            return redirect('admin_dashboard')
    else:
        form = AnnouncementForm()
    return render(request, 'dashboard/announcement_form.html', {'form': form, 'action': 'Add'})


@login_required
def admin_announcement_edit(request, pk):
    if not is_admin(request.user):
        messages.error(request, 'Access denied.')
        return redirect('home')
    ann = get_object_or_404(Announcement, pk=pk)
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, instance=ann)
        if form.is_valid():
            form.save()
            messages.success(request, 'Announcement updated!')
            return redirect('admin_dashboard')
    else:
        form = AnnouncementForm(instance=ann)
    return render(request, 'dashboard/announcement_form.html', {'form': form, 'action': 'Edit', 'announcement': ann})


@login_required
def admin_announcement_delete(request, pk):
    if not is_admin(request.user):
        messages.error(request, 'Access denied.')
        return redirect('home')
    ann = get_object_or_404(Announcement, pk=pk)
    if request.method == 'POST':
        ann.delete()
        messages.success(request, 'Announcement deleted.')
    return redirect('admin_dashboard')


@login_required
def admin_set_default_range(request):
    if not is_admin(request.user):
        messages.error(request, 'Access denied.')
        return redirect('home')
    default_range = DefaultDateRange.objects.filter(is_active=True).first()
    if request.method == 'POST':
        form = DefaultDateRangeForm(request.POST, instance=default_range)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.updated_by = request.user
            obj.save()
            messages.success(request, f'Default date range set to last {obj.days_back} days.')
            return redirect('admin_dashboard')
    else:
        form = DefaultDateRangeForm(instance=default_range)
    return render(request, 'dashboard/default_range_form.html', {'form': form})


@login_required
def admin_comment_delete(request, pk):
    if not is_admin(request.user):
        messages.error(request, 'Access denied.')
        return redirect('home')
    comment = get_object_or_404(Comment, pk=pk)
    if request.method == 'POST':
        comment.delete()
        messages.success(request, 'Comment deleted.')
    return redirect('admin_dashboard')


@login_required
def admin_set_net_balance(request):
    if not is_admin(request.user):
        messages.error(request, 'Access denied.')
        return redirect('home')
    net_balance = NetBalance.objects.order_by('-updated_at').first()
    if request.method == 'POST':
        form = NetBalanceForm(request.POST, instance=net_balance)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.updated_by = request.user
            obj.save()
            messages.success(request, 'Net balance updated successfully!')
            return redirect('admin_dashboard')
    else:
        form = NetBalanceForm(instance=net_balance)
    return render(request, 'dashboard/net_balance_form.html', {'form': form})


@login_required
def admin_user_manage(request, pk):
    if not is_admin(request.user):
        messages.error(request, 'Access denied.')
        return redirect('home')
    user_obj = get_object_or_404(User, pk=pk)
    profile, _ = UserProfile.objects.get_or_create(user=user_obj)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            user_obj.first_name = form.cleaned_data.get('first_name', user_obj.first_name)
            user_obj.last_name = form.cleaned_data.get('last_name', user_obj.last_name)
            user_obj.email = form.cleaned_data.get('email', user_obj.email)
            user_obj.save()
            form.save()
            messages.success(request, f'User {user_obj.username} updated!')
            return redirect('admin_dashboard')
    else:
        form = UserProfileForm(instance=profile, initial={
            'first_name': user_obj.first_name,
            'last_name': user_obj.last_name,
            'email': user_obj.email
        })
    return render(request, 'dashboard/user_form.html', {'form': form, 'user_obj': user_obj})


# ============================================================
# API / AJAX Views
# ============================================================

def income_api(request, pk):
    income = get_object_or_404(Income, pk=pk)
    return JsonResponse({
        'id': income.pk, 'source': income.source, 'source_name': income.source_name,
        'amount': str(income.amount), 'date': income.date.strftime('%Y-%m-%d'),
        'description': income.description, 'department': income.department,
        'display_name': income.get_display_name(),
    })


def expense_api(request, pk):
    expense = get_object_or_404(ExpenseRequest, pk=pk)
    return JsonResponse({
        'id': expense.pk, 'department': expense.department,
        'department_display': expense.get_department_display(),
        'category': expense.category, 'amount': str(expense.amount),
        'date': expense.date.strftime('%Y-%m-%d'), 'description': expense.description,
        'status': expense.status, 'status_display': expense.get_status_display(),
        'review_notes': expense.review_notes,
    })


def retirement_api(request, pk):
    retirement = get_object_or_404(Retirement, pk=pk)
    return JsonResponse({
        'id': retirement.pk, 'department': retirement.department,
        'department_display': retirement.get_department_display(),
        'category': retirement.category, 'amount': str(retirement.amount),
        'date': retirement.date.strftime('%Y-%m-%d'), 'description': retirement.description,
        'status': retirement.status, 'status_display': retirement.get_status_display(),
        'notes': retirement.notes,
    })
