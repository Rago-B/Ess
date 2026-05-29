# Voxlom EMS — Employee Management System
### By Voxlom Innovative Solutions

A full-stack Django Employee Management System with a modern dual-theme UI.

---

## 📁 Project Structure

```
voxlom_ems/
├── manage.py
├── requirements.txt
├── db.sqlite3              ← auto-created on first migrate
│
├── voxlom_ems/             ← Django project config
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── accounts/               ← Auth app
│   ├── __init__.py
│   ├── apps.py
│   ├── forms.py            ← RegistrationForm, LoginForm
│   ├── models.py           ← Uses built-in User model
│   ├── views.py            ← register, login, logout, dashboard
│   ├── urls.py
│   └── templates/
│       └── accounts/
│           ├── base.html
│           ├── login.html
│           ├── register.html
│           └── dashboard.html
│
└── static/
    ├── css/
    │   └── main.css        ← Full design system (light + dark)
    └── js/
        └── main.js         ← Theme, validation, password strength
```

---

## 🚀 Step-by-Step Setup

### Step 1 — Prerequisites
Make sure you have **Python 3.10+** installed:
```bash
python --version
```

### Step 2 — Create & activate a virtual environment
```bash
# Create
python -m venv venv

# Activate (macOS / Linux)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

### Step 3 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 4 — Apply database migrations
```bash
python manage.py migrate
```

### Step 5 — (Optional) Create an admin superuser
```bash
python manage.py createsuperuser
# Follow the prompts — this account gets the "Administrator" badge
```

### Step 6 — Run the development server
```bash
python manage.py runserver
```

### Step 7 — Open in browser
| URL | Page |
|-----|------|
| http://127.0.0.1:8000/ | Redirects to /login/ |
| http://127.0.0.1:8000/login/ | Login page |
| http://127.0.0.1:8000/register/ | Registration page |
| http://127.0.0.1:8000/dashboard/ | Protected dashboard |
| http://127.0.0.1:8000/logout/ | Logout |
| http://127.0.0.1:8000/admin/ | Django admin panel |

---

## 🎨 Features

### Authentication
- ✅ Register with First/Last Name, Username, Email, Password
- ✅ Login with **Username or Email**
- ✅ "Remember Me" session persistence
- ✅ Auto-login after registration
- ✅ Secure logout with confirmation message
- ✅ Dashboard route protected with `@login_required`

### Security
- ✅ Django CSRF protection on all forms
- ✅ Django's built-in password hashing (PBKDF2)
- ✅ Duplicate username/email validation
- ✅ Server-side + client-side form validation
- ✅ Password strength meter

### UI/UX
- ✅ **Dual theme** — Light & Dark (persisted in localStorage)
- ✅ OS preference detection on first visit
- ✅ Animated page transitions & card reveals
- ✅ Password show/hide toggle
- ✅ Auto-dismissing alert messages
- ✅ Fully responsive design

---

## 🔧 Adding Future Modules

The system is architected for easy expansion. For each new module (e.g., Attendance):

1. Create a new Django app: `python manage.py startapp attendance`
2. Add `'attendance'` to `INSTALLED_APPS` in `settings.py`
3. Extend the `User` model with a `OneToOneField` for employee profiles
4. Add the app's `urls.py` to `voxlom_ems/urls.py`
5. Add a nav link in `dashboard.html`

---

## 📝 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 4.2 (Python) |
| Auth | Django built-in auth (`django.contrib.auth`) |
| Database | SQLite (upgradeable to PostgreSQL) |
| Frontend | Django Templates + Vanilla JS |
| Fonts | Syne (display) + DM Sans (body) via Google Fonts |
| Theming | CSS Custom Properties (variables) |
| Timezone | Asia/Kolkata (IST) |
