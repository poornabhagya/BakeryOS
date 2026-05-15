# 🥐 BakeryOS - Bakery Management System

A complete full-stack web application for managing bakery operations including inventory, sales/POS, production batches, and analytics.

## 📊 Project Overview

```text
BakeryOS (Full Stack Application)
│
├── Backend/          Django REST API
│   └── Python 3.12+
│
└── Frontend/         React + TypeScript + Vite
    └── Node.js 18+
🎯 Features
👥 User Management
Role-based access (Manager, Cashier, Baker, Storekeeper)

Authentication via JWT

User dashboard per role

📦 Inventory Management
Product & ingredient tracking

Batch management with expiry dates

Automated Low-stock alerts

Stock history & audit trail

💳 Sales & POS
Shopping cart & checkout

Discount management

Payment methods tracking

Sales analytics & daily reports

🍰 Production & Wastage Tracking
Product batch creation and Recipe management

Advanced wastage logging (Products & Ingredients)

Base-unit cost calculations for accurate loss reporting

🚀 Quick Start Guide (Docker Recommended)
This project uses Docker to easily run the Frontend, Backend, and Database simultaneously without any manual environment setup.

Prerequisites
Install Docker Desktop and ensure it is running.

Setup Instructions
1. Environment Setup
Duplicate the .env.example file and rename it to .env (If not already provided in the zip). The default values are already configured for this Docker environment.

2. Build and Start the Application
Open your terminal (PowerShell/Command Prompt) in the project's root folder and run:

Bash
docker compose up --build -d
(Note: This will download the necessary images, install dependencies, and start the containers. This may take a few minutes the very first time.)

3. Run Database Migrations
Once the containers are running, set up the database schema by running:

Bash
docker compose exec backend python manage.py migrate
4. Create an Admin User
Generate a master login for the manager portal:

Bash
docker compose exec backend python manage.py createsuperuser
(Follow the prompt to enter an email, username, and password).

🌐 Accessing the App
Frontend / Manager Portal: http://localhost:3000

Backend API URL: http://localhost:8000/api/

Backend Admin Panel: http://localhost:8000/admin/

🛑 Stopping the App
To stop the servers safely without losing your database data, run:

Bash
docker compose down
💻 Manual Setup (Without Docker)
If you prefer to run the application locally without Docker, follow these steps:

Backend Setup:

Bash
cd Backend
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows PowerShell
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
Frontend Setup:

Bash
cd Frontend
npm install
npm run dev
🔐 Security
Environment Variables: Secrets in .env

JWT Authentication: Secure token-based auth

Role-Based Access Control: 4-tier permission system

SQL Injection Protection: Django ORM with parameterized queries

🗄️ Database Architecture
PostgreSQL: Primary database configured via Docker.

Models Overview:

Custom User Roles

Category, Product, & Ingredient Management

Batch Tracking & Expiry Logic

Sales, Billing, and Cart Management

Advanced Wastage & Notification Tracking

📚 Documentation & Technical References
SYSTEM_ARCHITECTURE.md - System design and logic flow.

DATABASE_SCHEMA.md - Complete database schema.

Status: Project Completed & Delivered ✅
Last Updated: April 2026