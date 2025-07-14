
# 🚀 Intern Management System (IMS)

The **Intern Management System (IMS)** is a RESTful web application built with **Django** and **Django REST Framework**. It enables organizations to efficiently manage their interns by providing role-based access, project/task tracking, OTP-based authentication, and automated weekly reports via email.

---

## 📚 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Roles & Permissions](#roles--permissions)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [Authentication](#authentication)
- [OTP Verification](#otp-verification)
- [Cron Jobs](#cron-jobs)
- [API Documentation](#api-documentation)
- [Contributing](#contributing)
- [License](#license)

---

## ✅ Features

- 🔐 JWT-based authentication using SimpleJWT
- 📩 Email-based OTP verification during user registration
- 🧑‍💼 Role-based access (Admin, Manager, Intern)
- 📊 Intern project/task assignment
- 📝 Daily reporting system for interns
- 📆 Automated weekly report email with Excel attachment via Celery
- 🧩 Modular app design following DRF standards

---

## 🛠️ Tech Stack

| Layer         | Technology             |
|---------------|-------------------------|
| Backend       | Django 4.x              |
| REST API      | Django REST Framework   |
| Auth          | JWT (SimpleJWT)         |
| Database      | PostgreSQL (or SQLite for dev) |
| Email Service | SMTP / Console backend  |
| Tasks         | Celery with Beat        |
| Worker Queue  | Redis (recommended)     |

---

## 🏗️ Architecture

```
├── accounts/
│   ├── models.py
│   ├── serializers.py
│   ├── permissions.py
│   └── utils/otp.py
├── templates/
├── mysite/ (project settings)
├── db.sqlite3
└── celery.py (configured with beat)
```

---

## 👥 Roles & Permissions

| Action                         | Admin | Manager | Intern |
|--------------------------------|:-----:|:-------:|:------:|
| Create/update projects         | ✅    | ✅      | ❌     |
| Assign/remove interns          | ✅    | ✅      | ❌     |
| Create/assign tasks            | ✅    | ✅      | ❌     |
| Submit daily work reports      | ❌    | ❌      | ✅     |
| View assigned tasks            | ✅    | ✅      | ✅     |
| View submitted reports         | ✅    | ✅      | ✅ (own only) |
| Register new users             | ✅    | ❌      | ❌     |
| OTP-based verification         | ✅    | ✅      | ✅     |

---

## ⚙️ Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/your-username/ims.git
cd ims
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Run the development server
```bash
python manage.py runserver
```

---

## 🔑 Environment Variables

Create a `.env` file based on this template:

```env
DEBUG=True
SECRET_KEY=your_secret_key
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@example.com
EMAIL_HOST_PASSWORD=your_password
```

---

## 🔐 Authentication

- JWT Authentication via **SimpleJWT**
- Use `/api/token/` to get access and refresh tokens
- Use `/api/token/refresh/` to refresh tokens

---

## 📩 OTP Verification

- OTP is generated and sent to the user's email on registration.
- Expires after 10 minutes.
- Users must verify OTP before being able to log in or get tokens.

---

## ⏰ Cron Jobs (Celery Beat)

- Weekly job scheduled every **Monday at 9:00 AM**
- Sends **Excel report** of intern activity to:
  - Each intern
  - Their respective project managers

---

## 📬 Sample Weekly Report Email

**Subject**: `Weekly Intern Report Summary - Project: Internal Tools`  
**Body**:
```
Dear Manager,

PFA for the weekly reports for interns assigned to your project.

Regards,  
Intern Management System
```

---

## 📘 API Documentation

- Swagger/OpenAPI or Postman collection to be included in `/docs` or root.
- Alternatively, generate using `drf_yasg` or `drf_spectacular`.

---

## 🤝 Contributing

Feel free to fork and contribute to this project via Pull Requests.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
