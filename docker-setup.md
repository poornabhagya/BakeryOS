# BakeryOS Docker Setup Guide (Full Stack)

This document is generated from your current project configuration:
- Backend: Django (in Backend), currently configured with python-decouple and SQLite default, PostgreSQL optional.
- Frontend: React + Vite (in Frontend), dev server on port 3000, API base in code is /api, and Vite proxy is currently hardcoded to http://localhost:8000.
- Goal: One-command startup for students with Docker Compose.

## 1) Expected Docker-Oriented Project Structure

Create these files in your existing structure:

```text
BakeryOS_Project/
├─ docker-compose.yml
├─ docker-setup.md
├─ Backend/
│  ├─ Dockerfile
│  ├─ .dockerignore
│  ├─ .env                  # Docker runtime env for Django
│  ├─ manage.py
│  ├─ requirements.txt
│  └─ core/
│     └─ settings.py
└─ Frontend/
   ├─ Dockerfile
   ├─ .dockerignore
   ├─ .env.docker           # Optional frontend env for docker dev
   ├─ package.json
   └─ vite.config.ts
```

## 2) Backend Dockerfile (Django)

Path: Backend/Dockerfile

This Dockerfile supports both development (runserver) and production-like (gunicorn) startup via DJANGO_ENV.

```dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# System packages for psycopg2 and build tools
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       libpq-dev \
       netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first for build cache efficiency
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip \
    && pip install -r /app/requirements.txt

# Copy project code
COPY . /app

EXPOSE 8000

# Development vs production-like startup from same image
# development: runserver
# production: gunicorn
CMD ["sh", "-c", "if [ \"$DJANGO_ENV\" = \"development\" ]; then python manage.py migrate && python manage.py runserver 0.0.0.0:8000; else python manage.py migrate && gunicorn core.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120; fi"]
```

## 3) Frontend Dockerfile (React/Vite)

Path: Frontend/Dockerfile

This is optimized for development sharing (hot-reload + Vite dev server).

```dockerfile
FROM node:20-alpine

WORKDIR /app

COPY package*.json /app/
RUN npm ci

COPY . /app

EXPOSE 3000

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3000"]
```

Optional production Dockerfile (if you later want static frontend served by Nginx):

Path: Frontend/Dockerfile.prod

```dockerfile
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json /app/
RUN npm ci
COPY . /app
RUN npm run build

FROM nginx:1.27-alpine
COPY --from=build /app/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## 4) Docker Compose (db + backend + frontend)

Path: docker-compose.yml

This is a complete one-command stack with:
- PostgreSQL persistence volume
- Backend connected to db service by service name
- Frontend connected to backend via Vite proxy target
- Startup ordering with DB healthcheck

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
      VITE_API_URL: http://localhost:3000/api
    volumes:
      - ./Frontend:/app
      - /app/node_modules
    ports:
      - "3000:3000"

volumes:
  postgres_data:
```

## 5) Required Environment + Code Changes

## 5.1 Backend .env for Docker

Path: Backend/.env

Use this for dockerized startup:

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

EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
REDIS_URL=redis://localhost:6379/0
```

## 5.2 Important Django settings.py fix for PostgreSQL

Your current DATABASES config always applies BASE_DIR / DB_NAME, which works for SQLite but is incorrect for PostgreSQL.

Update Backend/core/settings.py to use conditional logic:

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

## 5.3 Vite proxy change for Docker

Your current Frontend/vite.config.ts hardcodes:
- target: http://localhost:8000

Inside Docker, localhost means the frontend container itself, not backend. Replace with env-driven target:

```ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react-swc';
import path from 'path';

const apiProxyTarget = process.env.VITE_PROXY_TARGET || 'http://localhost:8000';

export default defineConfig({
  plugins: [react()],
  resolve: {
    extensions: ['.js', '.jsx', '.ts', '.tsx', '.json'],
    alias: {
      '@': path.resolve(__dirname, './src'),
      // keep your existing aliases unchanged
    },
  },
  build: {
    target: 'esnext',
    outDir: 'build',
  },
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
  },
});
```

## 6) .dockerignore Files (recommended)

Path: Backend/.dockerignore

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

Path: Frontend/.dockerignore

```dockerignore
node_modules/
build/
.git/
.gitignore
npm-debug.log*
.env.local
.env.*.local
```

## 7) Beginner Student Guide (Idiot-Proof)

## 7.1 Install Docker Desktop

1. Go to Docker Desktop official website.
2. Download Docker Desktop for your OS (Windows/Mac/Linux).
3. Install it with default settings.
4. Open Docker Desktop and wait until it says Docker Engine is running.
5. On Windows, make sure WSL2 integration is enabled (Docker usually prompts this automatically).

## 7.2 Get the Project

1. Download the project zip or clone the repository.
2. Open a terminal in the root folder (the folder containing docker-compose.yml).

## 7.3 First Startup (One Command)

Run:

```bash
docker compose up --build
```

What this does:
- Builds frontend and backend images
- Starts PostgreSQL
- Runs Django migrations automatically
- Starts Django API on port 8000
- Starts Vite frontend on port 3000

## 7.4 Open the App

- Frontend: http://localhost:3000
- Backend API root: http://localhost:8000/api/
- Django admin: http://localhost:8000/admin

## 7.5 Optional first-time admin user

Open a new terminal in project root and run:

```bash
docker compose exec backend python manage.py createsuperuser
```

## 7.6 Stop the project

Press Ctrl + C in the running terminal, then run:

```bash
docker compose down
```

If you also want to remove database data:

```bash
docker compose down -v
```

## 8) Quick Troubleshooting

- Port already in use:
  - Change host-side ports in docker-compose.yml (for example 3001:3000 or 8001:8000).

- Frontend cannot reach API:
  - Ensure VITE_PROXY_TARGET is set to http://backend:8000 in docker-compose.yml.
  - Ensure vite.config.ts uses process.env.VITE_PROXY_TARGET.

- Backend cannot connect to DB:
  - Confirm DB_HOST=db and DB_PORT=5432.
  - Confirm Postgres service is healthy.

- Migration errors after model changes:
  - Run:

```bash
docker compose exec backend python manage.py makemigrations
docker compose exec backend python manage.py migrate
```

## 9) Final Notes for Sharing with Students

- Students do not need local Python, Node, or PostgreSQL installed.
- They only need Docker Desktop and this project folder.
- Main startup command is exactly:

```bash
docker compose up --build
```

This setup is aligned with your current Django + Vite architecture and your current API usage pattern (/api with Vite proxy).
