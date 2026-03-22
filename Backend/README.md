# BakeryOS Backend API

Django REST Framework API for BakeryOS Bakery Management System.

## 🛠️ Tech Stack

- **Framework:** Django 6.0.3
- **API:** Django REST Framework 3.14.0
- **Authentication:** JWT (djangorestframework-simplejwt)
- **Database:** SQLite (dev), PostgreSQL (production)
- **API Documentation:** drf-spectacular
- **Task Queue:** Celery + Redis

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Virtual Environment (venv)

### Installation

```bash
# Navigate to Backend directory
cd Backend

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows PowerShell
# or
source venv/bin/activate     # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser (admin)
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

## 📖 Access Points

- **Admin Panel:** http://localhost:8000/admin
- **API Root:** http://localhost:8000/api/
- **API Docs:** http://localhost:8000/api/schema/swagger-ui/ (coming Phase 2)

## 📋 Project Structure

```
Backend/
├── core/              (Django configuration)
│   ├── settings.py   (settings with environment variables)
│   ├── urls.py       (main URL routing)
│   └── wsgi.py       (production WSGI)
│
├── api/               (Main application)
│   ├── models/       (Database models)
│   │   └── user.py   (Custom User model)
│   ├── views/        (API ViewSets)
│   ├── serializers/  (DRF Serializers)
│   ├── filters/      (Query filters)
│   ├── utils/        (Helper functions)
│   ├── signals.py    (Django signals)
│   └── migrations/   (Database migrations)
│
├── requirements.txt  (Python dependencies)
├── .env             (environment variables - ignored)
├── .env.example     (template - pushed to git)
└── manage.py        (Django CLI)
```

## 🔐 Environment Variables

Create `.env` file based on `.env.example`:

```
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

## 🗄️ Database

### Development
- **SQLite:** Auto-created as `db.sqlite3`

### Production
- **PostgreSQL:** Configure in `.env`

## 👤 User Roles

- **Manager** - Full system access
- **Cashier** - Sales & transactions
- **Baker** - Production & batch management
- **Storekeeper** - Inventory management

## 📋 API Endpoints (Phase 2+)

See [BACKEND_WORK_PLAN.md](BACKEND_WORK_PLAN.md) for complete endpoint specifications.

### Authentication (Coming)
- `POST /api/auth/login/`
- `POST /api/auth/refresh/`
- `POST /api/auth/logout/`

### Users (Coming)
- `GET /api/users/`
- `POST /api/users/`
- `GET /api/users/{id}/`
- `PUT /api/users/{id}/`

## 🧪 Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov
```

## 📚 Documentation

- [BACKEND_WORK_PLAN.md](BACKEND_WORK_PLAN.md) - Complete implementation plan
- [IMPLEMENTATION_CHECKLIST.md](IMPLEMENTATION_CHECKLIST.md) - Task tracking
- [TECHNICAL_REFERENCE.md](TECHNICAL_REFERENCE.md) - Code patterns
- [PHASE_1_COMPLETION_SUMMARY.md](PHASE_1_COMPLETION_SUMMARY.md) - Setup overview

## 💨 Development Workflow

```bash
# Create feature branch
git checkout -b feature/auth-endpoints

# Make changes, commit
git add .
git commit -m "feat(auth): Add login endpoint"

# Push and create PR
git push origin feature/auth-endpoints
```

## 🤝 Contributing

1. Create feature branch
2. Make changes
3. Write tests
4. Commit with descriptive message
5. Push and create Pull Request

## 📞 Support

For issues or questions, check the documentation or create an issue on GitHub.

---

**Last Updated:** March 22, 2026  
**Phase:** 1 (Setup Complete)  
**Status:** Ready for Phase 2
