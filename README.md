
# Intern Management System (IMS)

Intern Management System (IMS) is a RESTful web application built using **Django** and **Django REST Framework**. It allows organizations to manage interns, assign them to projects, track daily work logs, and generate weekly reports. This application supports role-based access for **Admin**, **Manager**, and **Intern** users.

---

## 🚀 Features

- 🔐 **Role-based Authentication** for Admins, Managers, and Interns
- 🧑‍💼 **Intern Registration & Profile Management**
- 📋 **Project Assignment** and Tracking
- 🕒 **Daily Work Logging** by Interns
- 📊 **Weekly Report Generation**
- 📮 **Email Notification** and OTP Verification
- ⏱️ **Scheduled Tasks** using Celery & Redis

---

## 🛠️ Tech Stack

- **Backend:** Django, Django REST Framework
- **Task Queue:** Celery with Redis
- **Database:** SQLite (dev), PostgreSQL (prod)
- **Containerization:** Docker
- **Others:** SMTP for email, Custom User Model

---

## ⚙️ Installation

### Prerequisites

- Python 3.9+
- Docker & Docker Compose (optional)
- Redis server (for Celery)

### Setup Locally

```bash
# Clone the repo
git clone https://github.com/your-username/IMS.git
cd IMS

# Create virtual environment and activate
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start the development server
python manage.py runserver
```

### Docker Setup

```bash
docker compose up --build
```

---

## 📬 Usage

- Admins can create managers and assign interns.
- Managers can assign tasks and monitor intern progress.
- Interns can log daily work and view assignments.
- Weekly summary reports are auto-generated using Celery.

---


## 🏗️ Architecture

```
├── accounts/
│   ├── models.py
│   ├── serializers.py
│   ├── permissions.py
│   └── utils/otp.py
├── templates/
├── models.py
├── mysite/ (project settings)
│   ├── celery.py (configured with beat) 
├── db.sqlite3
├── Dockerfile
```

## 📡 API Endpoints

Here are some key endpoints (refer to Postman collection or API docs for more):

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/register/` | POST | User registration |
| `/api/login/` | POST | Login and token generation |
| `/api/interns/` | GET/POST | Manage intern data |
| `/api/projects/` | GET/POST | Manage projects |
| `/api/daily-logs/` | POST | Log daily work |
| `/api/reports/weekly/` | GET | Generate weekly summary |

---

## 🤝 Contributing

1. Fork the project
2. Create a new branch (`git checkout -b feature/YourFeature`)
3. Commit your changes (`git commit -m 'Add some feature'`)
4. Push to the branch (`git push origin feature/YourFeature`)
5. Open a Pull Request

---

## 📧 Contact

For any queries or contributions, reach out via GitHub or email: [goutamaswani43@gmail.com]

---

*Built with ❤️ using Django & DRF*
