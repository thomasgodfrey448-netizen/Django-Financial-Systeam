from django.urls import path
from . import views

urlpatterns = [
    # Main dashboards
    path('', views.home_view, name='home'),
    path('income/', views.income_view, name='income'),
    path('expenses/', views.expense_view, name='expenses'),
    path('retirement/', views.retirement_view, name='retirement'),

    # Auth
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),

    # Income CRUD
    path('income/add/', views.income_add, name='income_add'),
    path('income/<int:pk>/edit/', views.income_edit, name='income_edit'),
    path('income/<int:pk>/detail/', views.income_detail, name='income_detail'),
    path('income/<int:pk>/delete/', views.income_delete, name='income_delete'),

    # Expense CRUD
    path('expenses/add/', views.expense_add, name='expense_add'),
    path('expenses/<int:pk>/edit/', views.expense_edit, name='expense_edit'),
    path('expenses/<int:pk>/detail/', views.expense_detail, name='expense_detail'),
    path('expenses/<int:pk>/delete/', views.expense_delete, name='expense_delete'),
    path('expenses/<int:pk>/status/', views.expense_status, name='expense_status'),

    # Retirement CRUD
    path('retirement/add/', views.retirement_add, name='retirement_add'),
    path('retirement/<int:pk>/edit/', views.retirement_edit, name='retirement_edit'),
    path('retirement/<int:pk>/detail/', views.retirement_detail, name='retirement_detail'),
    path('retirement/<int:pk>/delete/', views.retirement_delete, name='retirement_delete'),

    # Admin
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/announcement/add/', views.admin_announcement_add, name='announcement_add'),
    path('admin-panel/announcement/<int:pk>/edit/', views.admin_announcement_edit, name='announcement_edit'),
    path('admin-panel/announcement/<int:pk>/delete/', views.admin_announcement_delete, name='announcement_delete'),
    path('admin-panel/default-range/', views.admin_set_default_range, name='set_default_range'),
    path('admin-panel/net-balance/', views.admin_set_net_balance, name='set_net_balance'),
    path('admin-panel/user/<int:pk>/manage/', views.admin_user_manage, name='user_manage'),
    path('admin-panel/comment/<int:pk>/delete/', views.admin_comment_delete, name='admin_comment_delete'),

    # API endpoints
    path('api/income/<int:pk>/', views.income_api, name='income_api'),
    path('api/expense/<int:pk>/', views.expense_api, name='expense_api'),
    path('api/retirement/<int:pk>/', views.retirement_api, name='retirement_api'),
]
