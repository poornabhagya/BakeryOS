# 🥐 BakeryOS - Bakery Management System

A complete full-stack web application for managing bakery operations including inventory, sales/POS, production batches, and analytics.

## 📊 Project Overview

```
BakeryOS (Full Stack Application)
│
├── Backend/          Django REST API
│   └── Python 3.10+
│
└── Frontend/         React + TypeScript
    └── Node.js 16+
```

## 🎯 Features

### 👥 User Management
- 4 Role-based access (Manager, Cashier, Baker, Storekeeper)
- Authentication via JWT
- User dashboard per role

### 📦 Inventory Management
- Product & ingredient tracking
- Batch management with expiry dates
- Low-stock alerts
- Stock history/audit trail

### 💳 Sales & POS
- Shopping cart & checkout
- Discount management
- Payment methods tracking
- Sales analytics

### 🍰 Production
- Product batch creation
- Recipe management
- Ingredient requirements calculation
- Production tracking

### 🗑️ Wastage Tracking
- Product & ingredient wastage logging
- Wastage analytics
- Loss reporting by reason

### 📊 Analytics & Reporting
- Sales dashboards
- Revenue tracking
- Inventory analytics
- KPI metrics

## 🚀 Quick Start

### Backend Setup

```bash
cd Backend
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows PowerShell
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Access: http://localhost:8000/admin

### Frontend Setup

```bash
cd Frontend
npm install
npm run dev
```

Access: http://localhost:5173

## 📁 Project Structure

```
BakeryOS/
│
├── Backend/                    # Django REST API
│   ├── core/                   # Django configuration
│   ├── api/                    # Main application
│   │   ├── models/            # Database models
│   │   ├── views/             # API ViewSets
│   │   ├── serializers/       # DRF Serializers
│   │   ├── filters/           # Query filters
│   │   ├── utils/             # Helpers
│   │   └── signals.py
│   │
│   ├── requirements.txt        # Python dependencies
│   ├── .env.example           # Environment template
│   ├── README.md              # Backend docs
│   └── manage.py
│
├── Frontend/                   # React + TypeScript
│   ├── src/
│   │   ├── components/        # UI Components
│   │   ├── pages/             # Route pages
│   │   ├── context/           # React Context
│   │   ├── styles/            # CSS/Tailwind
│   │   ├── App.tsx
│   │   └── main.tsx
│   │
│   ├── package.json           # Node dependencies
│   ├── vite.config.ts        # Vite config
│   ├── tsconfig.json          # TypeScript config
│   ├── .env.example          # Environment template
│   └── README.md             # Frontend docs
│
├── .gitignore                # Git ignore rules
├── README.md                 # This file
└── docker-compose.yml        # (Optional) Docker setup

```

## 📋 Development Phases

### Phase 1: Setup ✅ COMPLETE
- Django project initialization
- Virtual environment setup
- User model creation
- Admin panel setup
- Database configuration

### Phase 2: Authentication ✅ COMPLETE
- JWT login/logout endpoints
- User CRUD API
- Permission classes
- Token refresh mechanism

### Phase 3: Inventory Setup ✅ COMPLETE
- Category models
- Ingredient management
- Batch management
- Product management
- Recipe management

### Phase 4-10: Features ✅ COMPLETE
- POS/Billing system
- Wastage tracking
- Audit trails
- Notifications
- Analytics
- Security hardening
- Testing & deployment

See [Backend/BACKEND_WORK_PLAN.md](Backend/BACKEND_WORK_PLAN.md) for detailed roadmap.

## 🔐 Security ✅ COMPLETE

- **Environment Variables:** Secrets in `.env` (not pushed)
- **JWT Authentication:** Secure token-based auth
- **Role-Based Access Control:** 4-tier permission system
- **CORS Configured:** Frontend origin whitelisted
- **SQL Injection Protection:** Django ORM with parameterized queries

## 🗄️ Database ✅ COMPLETE

### Development
- **SQLite:** `Backend/db.sqlite3`

### Production
- **PostgreSQL:** Configured in `.env`

### Models Overview
```
User (Custom User Model)
├── 4 Roles
├── Employee tracking
└── Status management

Category
├── Products
└── Ingredients

Product
├── Pricing & Stock
├── Recipes (ingredients needed)
└── Batches

Ingredient
├── Supplier tracking
├── Batches (expiry dates)
└── Stock history

Sales
├── Bill header with totals
├── Line items with prices
├── Discount tracking
└── Payment method

+ Wastage, Notifications, Stock History models
```

## 🤝 Contributing

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes
git add .
git commit -m "feat: description of what you added"

# Push to GitHub
git push origin feature/your-feature-name

# Create Pull Request on GitHub
```

### Commit Message Format
```
feat(scope): description       # New feature
fix(scope): description        # Bug fix
docs(scope): description       # Documentation
style(scope): description      # Code style
refactor(scope): description   # Code refactor
test(scope): description       # Tests
chore(scope): description      # Maintenance
```

Example:
```
feat(auth): Add JWT login endpoint
fix(inventory): Correct stock calculation
docs(api): Update API endpoints
```

## 📚 Documentation

- **[Backend/BACKEND_WORK_PLAN.md](Backend/BACKEND_WORK_PLAN.md)** - 10-phase implementation plan
- **[Backend/IMPLEMENTATION_CHECKLIST.md](Backend/IMPLEMENTATION_CHECKLIST.md)** - Task tracking
- **[Backend/TECHNICAL_REFERENCE.md](Backend/TECHNICAL_REFERENCE.md)** - Code patterns
- **[Backend/PHASE_1_COMPLETION_SUMMARY.md](Backend/PHASE_1_COMPLETION_SUMMARY.md)** - Phase 1 overview
- **[SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md)** - System design
- **[DATABASE_SCHEMA_CORRECTED.md](DATABASE_SCHEMA_CORRECTED.md)** - Database schema

## 💻 Technology Stack

### Backend
- **Django 6.0.3** - Web framework
- **Django REST Framework** - API framework
- **PostgreSQL / SQLite** - Database
- **JWT** - Authentication
- **Celery + Redis** - Async tasks
- **drf-spectacular** - API documentation

### Frontend
- **React 18+** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Axios** - HTTP client

## 🚀 Deployment

### Docker (Optional)
```bash
docker-compose up
```

### Manual Deployment
See [Backend/BACKEND_WORK_PLAN.md](Backend/BACKEND_WORK_PLAN.md) Phase 10 for detailed deployment instructions.

## 🐛 Troubleshooting

### Backend Issues
- See [Backend/README.md](Backend/README.md)

### Frontend Issues
- See [Frontend/README.md](Frontend/README.md)

## 📞 Support

For issues, questions, or contributions:
1. Check relevant README files
2. Review documentation
3. Create GitHub issue with clear description

## 📝 License

BakeryOS © 2026

---

## 🎯 Quick Links

- **Backend Setup:** [Backend/README.md](Backend/README.md)
- **Frontend Setup:** [Frontend/README.md](Frontend/README.md)
- **Implementation Plan:** [Backend/BACKEND_WORK_PLAN.md](Backend/BACKEND_WORK_PLAN.md)
- **System Architecture:** [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md)
- **Database Schema:** [DATABASE_SCHEMA_CORRECTED.md](DATABASE_SCHEMA_CORRECTED.md)

**Status:** Phase 1 Complete ✅ → Phase 2 Next 🔄

**Last Updated:** March 22, 2026
