# 🔒 BakeryOS Production Hardening Checklist

**Goal:** Get from 95% to 100% Production Ready  
**Estimated Time:** 8-12 hours  
**Difficulty:** Medium (mostly configuration)

---

## Phase 1: Environment Security (1-2 hours) 🔐

### HTTPS/SSL Setup
- [ ] Get SSL certificate (Let's Encrypt free option)
- [ ] Configure Django to enforce HTTPS in settings.py
  ```python
  SECURE_SSL_REDIRECT = True
  SESSION_COOKIE_SECURE = True
  CSRF_COOKIE_SECURE = True
  SECURE_HSTS_SECONDS = 31536000
  ```
- [ ] Update CORS_ALLOWED_ORIGINS to use `https://` instead of `http://`
- [ ] Update frontend API base URL to use HTTPS domain

### Security Headers
- [ ] Add Django Security Middleware checks
- [ ] Set Content-Security-Policy headers
- [ ] Add X-Frame-Options (clickjacking protection)
- [ ] Add X-Content-Type-Options (MIME sniffing protection)

### CORS Production Config
- [ ] Remove `localhost` from CORS_ALLOWED_ORIGINS
- [ ] Add only production domain(s)
- [ ] Set secure cookie SameSite=Strict
- [ ] Test cross-origin requests with curl

### API Rate Limiting
- [ ] Install `djangorestframework-throttling`
- [ ] Add throttle classes to settings:
  ```python
  REST_FRAMEWORK['DEFAULT_THROTTLE_CLASSES'] = [
      'rest_framework.throttling.AnonRateThrottle',
      'rest_framework.throttling.UserRateThrottle'
  ]
  REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {
      'anon': '100/hour',
      'user': '1000/hour'
  }
  ```
- [ ] Test rate limiting with concurrent requests

---

## Phase 2: Database & Backup (1-2 hours) 💾

### Backup Strategy
- [ ] Create backup automation script (PostgreSQL pg_dump)
  ```bash
  #!/bin/bash
  pg_dump bakeryos_db > /backups/bakeryos_$(date +%Y%m%d_%H%M%S).sql
  ```
- [ ] Schedule daily backups (cron job)
- [ ] Test backup restoration

### Database Connection Pool
- [ ] Configure connection pooling (pgbouncer or Django settings)
  ```python
  DATABASES = {
      'default': {
          'ENGINE': 'django.db.backends.postgresql',
          'CONN_MAX_AGE': 600,  # Connection pooling
          'OPTIONS': {
              'connect_timeout': 10,
          }
      }
  }
  ```

### Migration Safety
- [ ] Document all migration steps
- [ ] Create rollback procedures
- [ ] Test migrations in staging first

---

## Phase 3: Monitoring & Logging (2-3 hours) 📊

### Application Monitoring
- [ ] Set up Sentry for error tracking
  ```python
  # settings.py
  import sentry_sdk
  sentry_sdk.init(
      dsn="https://your-sentry-dsn@sentry.io/project",
      traces_sample_rate=1.0,
      environment="production"
  )
  ```
- [ ] Configure Sentry alerts for critical errors
- [ ] Test error reporting with test exception

### Logging Configuration
- [ ] Configure rotating file handler (RotatingFileHandler)
  ```python
  LOGGING = {
      'version': 1,
      'disable_existing_loggers': False,
      'handlers': {
          'file': {
              'level': 'INFO',
              'class': 'logging.handlers.RotatingFileHandler',
              'filename': '/logs/bakeryos.log',
              'maxBytes': 1024 * 1024 * 10,  # 10MB
              'backupCount': 10,
          },
      },
  }
  ```
- [ ] Set up log aggregation (Stackdriver, ELK, or Datadog)
- [ ] Create log viewing dashboard

### Frontend Error Tracking
- [ ] Install Sentry SDK in frontend
  ```typescript
  import * as Sentry from "@sentry/react";
  Sentry.init({ dsn: "your-dsn" });
  ```
- [ ] Wrap React app with Sentry ErrorBoundary
- [ ] Test error capture from frontend

### Health Check Endpoint
- [ ] Create `/health/` endpoint that checks:
  - [ ] Database connectivity
  - [ ] Cache status
  - [ ] External API status
  ```python
  @api_view(['GET'])
  def health_check(request):
      return Response({
          'status': 'healthy',
          'database': 'connected',
          'cache': 'available'
      })
  ```

---

## Phase 4: Performance Testing (2-3 hours) ⚡

### Load Testing
- [ ] Install locust load testing tool
  ```bash
  pip install locust
  ```
- [ ] Create load test scenarios:
  - [ ] Concurrent logins (100+ users)
  - [ ] Product list pagination (large dataset)
  - [ ] Sales creation under load
  - [ ] Concurrent cart operations
- [ ] Run test and identify bottlenecks
- [ ] Document acceptable load thresholds

### Performance Optimizations
- [ ] Enable database query optimization
  - Add `.select_related()` and `.prefetch_related()` 
  - Verify with django-debug-toolbar
- [ ] Add pagination limits (default max_page_size)
  ```python
  'MAX_PAGE_SIZE': 100
  ```
- [ ] Cache frequently accessed data (Redis)
  ```python
  CACHES = {
      'default': {
          'BACKEND': 'django.core.cache.backends.redis.RedisCache',
          'LOCATION': 'redis://127.0.0.1:6379/1',
      }
  }
  ```
- [ ] Compress API responses (GZip middleware)

### Frontend Optimization
- [ ] Build with production flag: `npm run build`
- [ ] Verify bundle size < 500KB
- [ ] Enable lazy loading for components
- [ ] Test on slow 3G network (DevTools)

---

## Phase 5: Security Audit (1-2 hours) 🛡️

### SQL Injection Prevention
- [ ] Verify all queries use parameterized statements
- [ ] Run OWASP ZAP security scan
- [ ] Test with SQL injection payloads on API endpoints

### XSS & CSRF Protection
- [ ] Verify CSRF tokens in forms
- [ ] Test with XSS payloads in inputs
- [ ] Check Content-Security-Policy headers
- [ ] Django CSRF middleware verified enabled

### Authentication Security
- [ ] Verify passwords never logged or exposed
- [ ] Test token expiration (access: 1hr, refresh: 7d)
- [ ] Verify refresh token rotation working
- [ ] Test logout clears all tokens

### API Security
- [ ] Verify API key rotation strategy
- [ ] Check for exposed secrets in code/logs
- [ ] Test API endpoints without auth headers
- [ ] Verify role-based access control (RBAC) working

### Dependency Vulnerabilities
- [ ] Run `pip audit` on backend dependencies
  ```bash
  pip audit
  ```
- [ ] Run `npm audit` on frontend dependencies
  ```bash
  npm audit
  ```
- [ ] Update vulnerable packages with known fixes

---

## Phase 6: Documentation & Deployment (1-2 hours) 📚

### API Documentation
- [ ] Generate OpenAPI schema (using drf-spectacular)
  ```python
  # settings.py
  INSTALLED_APPS = [..., 'drf_spectacular']
  ```
- [ ] Create Swagger/ReDoc endpoint: `/api/schema/swagger/`
- [ ] Document all 50+ endpoints with examples
- [ ] Include error response examples

### Deployment Runbook
- [ ] Create DEPLOYMENT.md with:
  - [ ] Prerequisites (Python version, PostgreSQL, Redis)
  - [ ] Step-by-step installation
  - [ ] Environment variable setup
  - [ ] Database migration procedure
  - [ ] Starting services (gunicorn, nginx)
  - [ ] SSL certificate installation
  - [ ] Monitoring setup

### Troubleshooting Guide
- [ ] Common issues and solutions:
  - [ ] Connection refused (port already in use)
  - [ ] Database authentication failed
  - [ ] Static files not loading
  - [ ] CORS errors
  - [ ] Token expiration issues
- [ ] How to check logs
- [ ] How to restart services
- [ ] How to rollback migrations

### Environment Setup
- [ ] `.env.production.example` file created
- [ ] Document all required vars:
  ```
  DEBUG=False
  SECRET_KEY=your-secret-key
  DATABASE_URL=postgresql://user:pass@host/dbname
  REDIS_URL=redis://localhost:6379
  SENTRY_DSN=https://...@sentry.io/...
  ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
  ```

---

## Phase 7: Testing & Validation (1-2 hours) ✅

### End-to-End Testing
- [ ] Test complete user flow:
  1. [ ] Open login page
  2. [ ] Valid credentials → dashboard
  3. [ ] Create product
  4. [ ] Create sale with product
  5. [ ] View sales summary
  6. [ ] Logout
  7. [ ] Login again (token refresh)
  8. [ ] Data persists
- [ ] Test with multiple roles (Manager, Cashier, Baker, Storekeeper)
- [ ] Test on mobile devices

### Error Scenario Testing
- [ ] Test invalid login 3x → account lock
- [ ] Test expired token → auto-refresh or re-login prompt
- [ ] Test network disconnect → graceful error
- [ ] Test 500 error from backend → user message
- [ ] Test concurrent operations (race conditions)

### Browser Compatibility
- [ ] Test on Chrome (latest)
- [ ] Test on Firefox (latest)
- [ ] Test on Safari (latest)
- [ ] Test on mobile Safari (iOS)
- [ ] Test on Chrome Mobile (Android)

### Accessibility Testing
- [ ] Run lighthouse audit (`npm run build` → lighthouse)
- [ ] Verify keyboard navigation (Tab through forms)
- [ ] Test with screen reader (NVDA/VoiceOver)
- [ ] Check color contrast ratios (WCAG AA)

---

## 📋 Pre-Launch Checklist

### Backend Requirements ✅
- [ ] `python manage.py makemigrations` (no pending)
- [ ] `python manage.py migrate` (all migrations applied)
- [ ] `python manage.py check --deploy` (security issues = 0)
- [ ] `python manage.py collectstatic` (if using S3)
- [ ] No hardcoded secrets in code
- [ ] `.env` file created (NOT in git)
- [ ] `requirements.txt` up to date

### Frontend Requirements ✅
- [ ] `npm run build` succeeds (0 errors)
- [ ] `npm audit` shows no critical vulnerabilities
- [ ] API base URL points to production
- [ ] Feature flags for beta features set to false
- [ ] Google Analytics/Sentry DSN configured
- [ ] No console errors in production build

### Infrastructure ✅
- [ ] Server/hosting set up (Linode, AWS, DigitalOcean, Heroku)
- [ ] Domain DNS configured
- [ ] SSL certificate installed
- [ ] PostgreSQL database created and migrated
- [ ] Redis cache available
- [ ] Backups automated and tested
- [ ] Monitoring/alerting configured

### Documentation ✅
- [ ] API documentation complete
- [ ] Deployment runbook signed off
- [ ] Troubleshooting guide reviewed
- [ ] Team trained on ops procedures

---

## 🎯 Success Criteria (100% Production Ready)

- [ ] All 11 integration issues resolved ✅ (DONE)
- [ ] Build: 0 TypeScript errors ✅ (DONE)
- [ ] Backend: 0 Django issues ✅ (DONE)
- [ ] HTTPS/SSL enabled ✅ (NEW)
- [ ] Database backups automated ✅ (NEW)
- [ ] Error monitoring active (Sentry) ✅ (NEW)
- [ ] Load testing passed ✅ (NEW)
- [ ] Security audit passed ✅ (NEW)
- [ ] API documentation complete ✅ (NEW)
- [ ] E2E tests pass on all scenarios ✅ (NEW)
- [ ] No console errors in production ✅ (NEW)
- [ ] Team trained on deployment ✅ (NEW)

---

## 📞 Next Steps

**Choose your priority:**

1. **Fast Track (4 hours):** Essentials only
   - SSL/HTTPS
   - Basic monitoring (Sentry)
   - Load testing (light)
   - Deployment docs

2. **Standard Track (8 hours):** Recommended for most projects
   - All Phase 1-6 items
   - Full security audit
   - Full E2E testing

3. **Enterprise Track (12 hours):** Full compliance
   - All items above +
   - Penetration testing
   - Compliance audit (GDPR/SOC2)
   - Disaster recovery drill

---

**Status:** Ready to start. Which phase would you like to tackle first?

**Report Generated:** March 26, 2026  
**Target Completion:** March 27, 2026 (for 100% production-ready)
