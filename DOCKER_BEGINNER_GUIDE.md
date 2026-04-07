# Docker Beginner Guide for BakeryOS (Step by Step)

This guide is written for a complete beginner.
You do not need Python, Node, or PostgreSQL installed locally.
You only need Docker Desktop.

Goal:
Run your full project (Frontend + Backend + PostgreSQL) with one command:

```bash
docker compose up --build
```

---

## 1. What Docker Is (Simple Explanation)

1. Docker lets you run apps in containers.
2. A container is like a mini-computer for one app.
3. Your project has 3 parts that will run in 3 containers:
   1. Frontend container (React/Vite)
   2. Backend container (Django)
   3. Database container (PostgreSQL)
4. Docker Compose is a file that starts all 3 together.

---

## 2. One-Time Setup on Your Laptop

## 2.1 Install Docker Desktop

1. Open: https://www.docker.com/products/docker-desktop/
2. Download Docker Desktop for Windows.
3. Install with default options.
4. If WSL2 prompt appears, allow it.
5. Restart PC if installer asks.
6. Open Docker Desktop.
7. Wait until status says Docker Engine is running.

## 2.2 Test Docker Installation

Open PowerShell and run:

```powershell
docker --version
docker compose version
```

If both commands print version numbers, you are ready.

---

## 3. Your Project Folder

Make sure you are in your project root:

```powershell
cd "C:\Projects\campus project\BakeryOS_Project"
```

You should see folders named Backend and Frontend.

---

## 4. Files You Must Create for Docker

You will create these files manually:

1. Backend/Dockerfile
2. Frontend/Dockerfile
3. docker-compose.yml
4. Backend/.dockerignore
5. Frontend/.dockerignore
6. Backend/.env (if not already present, create/update for Docker)

---

## 5. Create Backend Dockerfile

Create file: Backend/Dockerfile

Paste this:

```dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       libpq-dev \
       netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip \
    && pip install -r /app/requirements.txt

COPY . /app

EXPOSE 8000

CMD ["sh", "-c", "if [ \"$DJANGO_ENV\" = \"development\" ]; then python manage.py migrate && python manage.py runserver 0.0.0.0:8000; else python manage.py migrate && gunicorn core.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120; fi"]
```

---

## 6. Create Frontend Dockerfile

Create file: Frontend/Dockerfile

Paste this:

```dockerfile
FROM node:20-alpine

WORKDIR /app

COPY package*.json /app/
RUN npm ci

COPY . /app

EXPOSE 3000

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3000"]
```

---

## 7. Create docker-compose.yml (Main File)

Create file: docker-compose.yml in root folder.

Paste this:

```yaml
version: "3.9"

services:
  db:
    image: postgres:16-alpine
    container_name: bakeryos_db
    restart: unless-stopped
    environment:
      POSTGRES_DB: bakeryos_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d bakeryos_db"]
      interval: 5s
      timeout: 5s
      retries: 20

  backend:
    build:
      context: ./Backend
      dockerfile: Dockerfile
    container_name: bakeryos_backend
    restart: unless-stopped
    depends_on:
      db:
        condition: service_healthy
    env_file:
      - ./Backend/.env
    environment:
      DJANGO_ENV: development
      DEBUG: "True"
      SECRET_KEY: docker-dev-secret-key-change-me
      ALLOWED_HOSTS: localhost,127.0.0.1,backend
      DB_ENGINE: django.db.backends.postgresql
      DB_NAME: bakeryos_db
      DB_USER: postgres
      DB_PASSWORD: postgres
      DB_HOST: db
      DB_PORT: "5432"
      CORS_ALLOWED_ORIGINS: http://localhost:3000,http://127.0.0.1:3000
      CSRF_TRUSTED_ORIGINS: http://localhost:3000,http://127.0.0.1:3000
    volumes:
      - ./Backend:/app
    ports:
      - "8000:8000"

  frontend:
    build:
      context: ./Frontend
      dockerfile: Dockerfile
    container_name: bakeryos_frontend
    restart: unless-stopped
    depends_on:
      - backend
    environment:
      CHOKIDAR_USEPOLLING: "true"
      VITE_PROXY_TARGET: http://backend:8000
    volumes:
      - ./Frontend:/app
      - /app/node_modules
    ports:
      - "3000:3000"

volumes:
  postgres_data:
```

---

## 8. Create .dockerignore Files

## 8.1 Backend/.dockerignore

```dockerignore
__pycache__/
*.pyc
*.pyo
*.pyd
*.sqlite3
db.sqlite3
.env
venv/
.pytest_cache/
.git/
.gitignore
media/
staticfiles/
```

## 8.2 Frontend/.dockerignore

```dockerignore
node_modules/
build/
.git/
.gitignore
npm-debug.log*
.env.local
.env.*.local
```

---

## 9. Update Backend .env for Docker DB

Open Backend/.env and ensure these values exist:

```env
DEBUG=True
SECRET_KEY=docker-dev-secret-key-change-me
ALLOWED_HOSTS=localhost,127.0.0.1,backend

DB_ENGINE=django.db.backends.postgresql
DB_NAME=bakeryos_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
CSRF_TRUSTED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

---

## 10. Important Code Fix #1 (Django settings.py)

Your current settings can break PostgreSQL in Docker because SQLite path logic is reused.

Open Backend/core/settings.py and replace the DATABASES block with this:

```python
DB_ENGINE = config('DB_ENGINE', default='django.db.backends.sqlite3')

if DB_ENGINE == 'django.db.backends.sqlite3':
    DATABASES = {
        'default': {
            'ENGINE': DB_ENGINE,
            'NAME': BASE_DIR / config('DB_NAME', default='db.sqlite3'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': DB_ENGINE,
            'NAME': config('DB_NAME', default='bakeryos_db'),
            'USER': config('DB_USER', default='postgres'),
            'PASSWORD': config('DB_PASSWORD', default='postgres'),
            'HOST': config('DB_HOST', default='db'),
            'PORT': config('DB_PORT', default='5432'),
        }
    }
```

---

## 11. Important Code Fix #2 (Vite proxy for Docker)

Your Frontend/vite.config.ts currently proxies to localhost:8000.
Inside Docker, that localhost is wrong.

Open Frontend/vite.config.ts and change the proxy target to env-driven:

```ts
const apiProxyTarget = process.env.VITE_PROXY_TARGET || 'http://localhost:8000';
```

Then in server.proxy use:

```ts
'/api': {
  target: apiProxyTarget,
  changeOrigin: true,
}
```

Also ensure server host is exposed:

```ts
server: {
  host: '0.0.0.0',
  port: 3000,
  open: false,
  proxy: {
    '/api': {
      target: apiProxyTarget,
      changeOrigin: true,
    },
  },
}
```

---

## 12. Build and Run Everything

From project root:

```powershell
docker compose up --build
```

First run can take a few minutes.

When successful, you should see logs from:
1. db
2. backend
3. frontend

---

## 13. Open URLs

1. Frontend app: http://localhost:3000
2. Backend API: http://localhost:8000/api/
3. Django admin: http://localhost:8000/admin

---

## 14. Create Admin User (First Time)

Open new terminal in root and run:

```powershell
docker compose exec backend python manage.py createsuperuser
```

Follow prompts for username and password.

---

## 15. Daily Use Commands

Start project:

```powershell
docker compose up
```

Stop project:

```powershell
docker compose down
```

Rebuild after changing Dockerfile or dependencies:

```powershell
docker compose up --build
```

See container status:

```powershell
docker compose ps
```

See logs:

```powershell
docker compose logs -f
```

Run Django migration manually:

```powershell
docker compose exec backend python manage.py migrate
```

---

## 16. Common Problems and Fixes

## 16.0 Error: No matching distribution found for Django==6.0.3

Cause:
1. Django 6 requires Python 3.12+.
2. If Dockerfile uses python:3.11-slim, install fails exactly like your error.

Fix:
1. Open Backend/Dockerfile.
2. Change first line to:

```dockerfile
FROM python:3.12-slim
```

3. Rebuild without cache:

```powershell
docker compose build --no-cache backend
docker compose up --build
```

## 16.1 Port Already in Use

Error like "port 3000 is already allocated".

Fix:
1. Stop existing app using that port.
2. Or change compose ports.

Example:
- "3001:3000" for frontend
- "8001:8000" for backend

Then open new port in browser.

## 16.2 Frontend Shows API Errors

Usually proxy target issue.

Check:
1. VITE_PROXY_TARGET in compose is http://backend:8000
2. vite.config.ts uses process.env.VITE_PROXY_TARGET
3. Rebuild with docker compose up --build

## 16.3 Backend Cannot Connect to DB

Check:
1. DB_HOST is db
2. DB_PORT is 5432
3. Postgres container is healthy

Run:

```powershell
docker compose ps
```

## 16.4 Need Fresh Database

Warning: this deletes all DB data.

```powershell
docker compose down -v
docker compose up --build
```

---

## 17. What You Learned (Quick Recap)

1. Dockerfile defines how each service image is built.
2. docker-compose.yml defines how services run together.
3. Containers communicate by service name (backend, db), not localhost.
4. Volumes keep your PostgreSQL data safe between restarts.
5. One command can run full stack for any student.

---

## 18. Final Student Sharing Steps

When sharing with a university student:

1. Share full project folder including Docker files.
2. Tell them to install Docker Desktop only.
3. Tell them to run from root:

```powershell
docker compose up --build
```

That is all.
