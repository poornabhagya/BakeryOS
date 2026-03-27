# 🔍 Quick Login Response Diagnostic

**Paste this in your Browser Console (F12) and run it:**

```javascript
// Clear old data
localStorage.clear();

// Test login
console.log('=== Testing Login Response ===');

fetch('http://localhost:8000/api/auth/login/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    username: 'cashier1',
    password: 'testpassword123'
  })
})
.then(response => {
  console.log('Raw Status:', response.status);
  console.log('Content-Type Header:', response.headers.get('content-type'));
  return response.text(); // Get raw response first
})
.then(text => {
  console.log('=== RAW RESPONSE ===');
  console.log(text);
  console.log('=== END RAW ===');
  
  try {
    const data = JSON.parse(text);
    console.log('=== PARSED JSON ===');
    console.log(data);
    console.log('Keys in response:', Object.keys(data));
    
    if (data.access) console.log('✅ HAS access:', data.access.substring(0, 20) + '...');
    else console.log('❌ NO access field');
    
    if (data.refresh) console.log('✅ HAS refresh:', data.refresh.substring(0, 20) + '...');
    else console.log('❌ NO refresh field');
    
    if (data.user) console.log('✅ HAS user:', data.user);
    else console.log('❌ NO user field');
    
  } catch (e) {
    console.error('Failed to parse JSON:', e);
    console.log('Response might be HTML or plain text');
  }
})
.catch(err => console.error('Request failed:', err));
```

---

## What to Do

1. **Open DevTools (F12)**
2. **Go to Console tab**
3. **Copy the code above and paste it**
4. **Press Enter**
5. **Tell me what you see:**

**You should see output like:**
```
Raw Status: 200
Content-Type Header: application/json
=== RAW RESPONSE ===
{"access":"eyJ0eXAi...","refresh":"eyJ0eXAi...","user":{"id":19,...}}
=== PARSED JSON ===
{...parsed object...}
Keys in response: access,refresh,user
✅ HAS access: eyJ0eXAiOiJKV1Qi...
✅ HAS refresh: eyJ0eXAiOiJKV1Qi...
✅ HAS user: {...}
```

---

## If You See Different Output

**Tell me:**
1. What is the Raw Status? (should be 200)
2. What is the Content-Type? (should be `application/json`)
3. What keys are IN the response? (should include `access`, `refresh`, `user`)
4. If response is HTML instead of JSON - what does it show?

Once I see this, I'll know exactly what's wrong!
