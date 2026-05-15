# 🔍 Authentication Debug Guide

## Quick Debug Steps

### Step 1: Check Browser LocalStorage After Login

1. **Login to the system** with credentials you tried
2. **Open DevTools** (F12 in Chrome/Firefox)
3. **Go to Application tab** → **LocalStorage** → **http://localhost:5173**
4. **Look for these keys:**

```
☐ access_token  (should have a long JWT string starting with "eyJ...")
☐ refresh_token (should have a long JWT string)
☐ bakeryUser    (should have user data JSON)
```

**If ANY of these are MISSING → This is the bug!**

---

### Step 2: Check Browser Console for [API] Messages

1. **Open DevTools Console** (F12)
2. **Try to perform an action** that requires auth (e.g., click on Dashboard after login)
3. **Look for console messages** starting with `[API]`

**You should see something like:**
```
[API] Token expired on /api/products/?page=1, attempting refresh...
[API] GET /api/products/?page=1 200 OK
```

**If you see instead:**
```
[API] Unauthorized access on /api/products/?page=1 - clearing session
```

→ **Token is not being stored!**

---

### Step 3: Check Network Tab

1. **Open DevTools** → **Network tab**
2. **Clear network history**
3. **Login again**
4. **Look at the login POST response**
5. **Click Response tab** and verify you see:
   - `"access": "eyJ..."`
   - `"refresh": "eyJ..."`
   - `"user": {...}`

**If you DON'T see this → Backend is not returning tokens!**

---

## Common Issues & Fixes

### Issue 1: Tokens Not In LocalStorage After Login

**Symptom:**
- Login succeeds (200 status)
- Next API call gets 401
- localStorage has NO access_token

**Cause:** `setTokens()` is not being called or is failing

**Fix:** Check that `authApi.login()` is properly returning the response

---

### Issue 2: Wrong Backend Response Format

**Symptom:**
- Login 200 but response doesn't match expected format

**Backend Issue:** Response might have different field names

**Check:** Your Django response should be:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLC...",
  "refresh": "eyJ0eXAiOiJKV1QiLC...",
  "user": {
    "id": 1,
    "username": "cashier1",
    "full_name": "...",
    "role": "Cashier"
  }
}
```

**If your response has different keys:**
- Change the api.ts to match your backend
- Example: if your backend returns `access_token` instead of `access`, update api.ts

---

### Issue 3: CORS Not Sending Authorization Header

**Symptom:**
- Authorization header not sent in requests
- CORS error in console

**Check Backend `settings.py`:**
```python
CORS_ALLOWED_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',  # ← MUST include this
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]
```

---

### Issue 4: Token Stored But Backend Rejects It

**Symptom:**
- localStorage HAS access_token
- But API returns 401

**Possible Causes:**
1. **Token format wrong:** Should be `"Bearer eyJ0eXAi..."`
2. **Token expired:** Check token lifetime in settings.py
3. **Token wrong type:** Backend might expect different JWT structure

**Check:** In Network tab, look at GET /api/products/ request:
- **Headers** tab should show: `Authorization: Bearer eyJ0eXAi...`

**If you see:**
- `Authorization: eyJ0eXAi` (no "Bearer") → need to add "Bearer " prefix
- NO Authorization header at all → tokens not being read from storage

---

## File-by-File Checklist

### Frontend (src/services/api.ts)

Check that these exist and are correct:

```typescript
// ✓ Check 1: Token storage after login
export function setTokens(access: string, refresh: string) {
  accessToken = access;
  refreshToken = refresh;
  localStorage.setItem('access_token', access);     // ← Must save to localStorage
  localStorage.setItem('refresh_token', refresh);   // ← Must save to localStorage
}

// ✓ Check 2: Token retrieval
export function getAccessToken(): string | null {
  return accessToken || localStorage.getItem('access_token');  // ← Falls back to localStorage
}

// ✓ Check 3: Authorization header includes "Bearer "
function getAuthHeaders(): Record<string, string> {
  const token = getAccessToken();
  return {
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Bearer ${token}` }),  // ← "Bearer " prefix important
  };
}

// ✓ Check 4: Login endpoint stores tokens
export const authApi = {
  login: async (username: string, password: string) => {
    const response = await makeRequest(...)
    setTokens(response.access, response.refresh);  // ← Must call setTokens()
    return response;
  },
}
```

### Backend (core/settings.py)

```python
# ✓ Check 1: JWT is configured
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',  # ← Must be this
    ),
}

# ✓ Check 2: CORS allows Authorization header
CORS_ALLOWED_HEADERS = [..., 'authorization', ...]

# ✓ Check 3: JWT tokens have reasonable lifetime
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),    # ← Should not be 0 seconds
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),    # ← Should not be 0 days
}
```

---

## Test Script to Add to Browser Console

**Paste this in browser Console (F12) after logging in:**

```javascript
console.log('=== Auth Debug ===');
console.log('access_token:', localStorage.getItem('access_token'));
console.log('refresh_token:', localStorage.getItem('refresh_token'));
console.log('bakeryUser:', localStorage.getItem('bakeryUser'));

// Try making an API call
fetch('http://localhost:8000/api/products/?page=1', {
  headers: {
    'Authorization': 'Bearer ' + localStorage.getItem('access_token'),
    'Content-Type': 'application/json'
  }
})
.then(r => {
  console.log('Response status:', r.status);
  return r.json();
})
.then(d => console.log('Response data:', d))
.catch(e => console.error('Error:', e));
```

**Expected output:**
```
access_token: eyJ0eXAiOiJKV1QiLC...
refresh_token: eyJ0eXAiOiJKV1QiLC...
bakeryUser: {"id":1,"username":"cashier1"...}
Response status: 200
Response data: {count: 50, results: [...]}
```

---

## Most Common Cause

**99% of the time, the issue is:**

The `setTokens()` function in api.ts is NOT being called after login, so localStorage never gets the tokens.

**Check:**
1. Does `authApi.login()` return `{access, refresh, user}`?
2. Is the response being passed to `setTokens(response.access, response.refresh)`?
3. Are the response field names correct? (not `access_token`, `jwt_token`, etc.?)

---

## Next Steps

**After you debug with steps above, tell me:**

1. ✅ / ❌ Are tokens in localStorage after login?
2. ✅ / ❌ Does GET request include Authorization header?
3. ✅ / ❌ When you check Network tab, what does login response show?
4. ✅ / ❌ What's the exact error in console?

**Then I'll fix the issue!**
