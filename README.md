# Maarifa Finance Dashboard

A professional Django-based Financial Management System featuring income tracking, expense requests, retirement fund management, and role-based access control. All amounts are displayed in **TSH (Tanzanian Shilling)** format `(0,000,000.00)`.

---

## Features

### Dashboards
| Dashboard | Description |
|-----------|-------------|
| **Home** | Overview with 4 summary cards (Income, Expenses, Retirement, Net Balance), announcements, and comment box |
| **Income** | Track Zaka, Sadaka, MK and other income with date filtering and department breakdown |
| **Expenses Request** | Submit and manage expense requests with approval status (Pending/Approved/Not Approved) |
| **Retirement** | Track retirement fund records with Open/Closed status |
| **Admin Panel** | Full control panel for admins with tabbed sections for all data management |

### Key Features
- **TSH Currency Format**: All amounts displayed as `0,000,000.00`
- **Date Filtering**: Filter all dashboards by date range (From - To)
- **Department Filter**: 10 departments available for filtering
- **Role-Based Access**: Admin and User roles with different permissions
- **Default Date Range**: Admin can set default date range (e.g., last 7-14 days)
- **Responsive Design**: Professional layout for both desktop and mobile
- **CRUD Operations**: Add, Edit, View, Delete records with modal forms
- **Status Management**: Change expense status (Pending/Approved/Not Approved) and retirement status (Open/Closed)
- **Announcements**: Admin can add/edit/delete announcements shown on home dashboard
- **Comments**: Public comment box on home dashboard
- **Professional Footer**: Organization info and navigation links

---

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Backend | Django 5.x (Python 3.11) |
| Frontend | Bootstrap 5.3, Font Awesome 6.5, Chart.js 4.4 |
| Database | SQLite3 (development) |
| CSS | Custom professional dark-blue/white theme |
| JavaScript | Vanilla JS with Bootstrap modals and AJAX |
| Fonts | Google Fonts - Inter |

---

## Installation & Setup

### Prerequisites
- Python 3.11+
- pip

### Step 1: Clone or extract the project
```bash
cd financial_dashboard
```

### Step 2: Create a virtual environment (recommended)
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows
```

### Step 3: Install dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run migrations
```bash
python manage.py migrate
```

### Step 5: Create a superuser (admin)
```bash
python manage.py createsuperuser
```

### Step 6: Load sample data (optional)
```bash
python manage.py shell < seed_data.py
```

### Step 7: Run the development server
```bash
python manage.py runserver
```

### Step 8: Open in browser
```
http://localhost:8000/
```

---

## Default Login Credentials (after seeding)

| Role | Username | Password |
|------|----------|----------|
| Admin | `admin` | `admin123` |
| User | `user1` | `user1234` |

> **Important**: Change these credentials in production!

---

## Project Structure

```
financial_dashboard/
├── config/                  # Django project configuration
│   ├── settings.py          # Settings (CSRF, DB, static files)
│   ├── urls.py              # Main URL configuration
│   └── wsgi.py
├── dashboard/               # Main application
│   ├── models.py            # Database models
│   ├── views.py             # View functions
│   ├── urls.py              # App URL patterns
│   ├── forms.py             # Django forms
│   └── admin.py             # Django admin registration
├── templates/               # HTML templates
│   ├── base.html            # Base layout with navbar and footer
│   ├── registration/
│   │   ├── login.html       # Login page
│   │   └── register.html    # Registration page
│   └── dashboard/
│       ├── home.html        # Home dashboard
│       ├── income.html      # Income dashboard
│       ├── expenses.html    # Expenses dashboard
│       ├── retirement.html  # Retirement dashboard
│       ├── admin_dashboard.html  # Admin control panel
│       ├── income_form.html      # Add/Edit income form
│       ├── expense_form.html     # Add/Edit expense form
│       ├── retirement_form.html  # Add/Edit retirement form
│       ├── income_detail.html    # Income record detail
│       ├── expense_detail.html   # Expense record detail
│       ├── retirement_detail.html # Retirement record detail
│       ├── announcement_form.html # Announcement form
│       ├── default_range_form.html # Default date range settings
│       └── user_form.html        # User management form
├── static/
│   ├── css/
│   │   └── dashboard.css    # Professional dark-blue/white theme
│   └── js/
│       └── dashboard.js     # Interactive features and AJAX
├── manage.py
├── requirements.txt
└── README.md
```

---

## Departments (10)

1. Administration
2. Finance
3. Education
4. Health
5. Welfare
6. Youth & Sports
7. Women's Affairs
8. Security
9. Infrastructure
10. Communications

---

## User Roles & Permissions

| Feature | Public | User (Logged In) | Admin |
|---------|--------|-----------------|-------|
| View all dashboards | ✅ | ✅ | ✅ |
| View records | ✅ | ✅ | ✅ |
| Add income records | ❌ | ✅ | ✅ |
| Add expense requests | ❌ | ✅ | ✅ |
| Add retirement records | ❌ | ✅ | ✅ |
| Edit records | ❌ | ✅ | ✅ |
| Change expense status | ❌ | ✅ | ✅ |
| Delete records | ❌ | ❌ | ✅ |
| Manage announcements | ❌ | ❌ | ✅ |
| Set default date range | ❌ | ❌ | ✅ |
| Manage users | ❌ | ❌ | ✅ |
| Access admin panel | ❌ | ❌ | ✅ |

---

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/income/<pk>/` | Get income record as JSON |
| `GET /api/expense/<pk>/` | Get expense record as JSON |
| `GET /api/retirement/<pk>/` | Get retirement record as JSON |

---

## Configuration

### Default Date Range
Admins can set the default date range shown on all dashboards via **Admin Panel > Settings**. The default is the last 14 days.

### CSRF Trusted Origins
For deployment behind a proxy, update `CSRF_TRUSTED_ORIGINS` in `config/settings.py`:
```python
CSRF_TRUSTED_ORIGINS = [
    'https://yourdomain.com',
]
```

---

## Production Deployment Notes

1. Set `DEBUG = False` in `settings.py`
2. Set a strong `SECRET_KEY`
3. Configure a production database (PostgreSQL recommended)
4. Run `python manage.py collectstatic`
5. Use Gunicorn + Nginx for serving
6. Set proper `ALLOWED_HOSTS`

---

## License

This project is built for Maarifa Finance organization. All rights reserved.

&copy; 2024 Maarifa Finance - Tanzania
