# POS 400 Bad Request - Quick Fix Guide

## 🔴 Error: `POST https://api.marinapizzas.com.au/graphql/ 400 (Bad Request)`

This error means the GraphQL request failed. The most common cause is **authentication**.

---

## ✅ Quick Fix Steps

### **Step 1: Check if User is Logged In**

Open browser console and run:

```javascript
fetch('https://api.marinapizzas.com.au/graphql/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  credentials: 'include',
  body: JSON.stringify({
    query: `query { me { id username role isStaffMember } }`
  })
})
.then(r => r.json())
.then(data => {
  console.log('Current user:', data);
  if (!data.data.me) {
    console.error('❌ NOT LOGGED IN - You need to login first!');
  } else {
    console.log('✅ Logged in as:', data.data.me);
  }
});
```

**If `data.data.me` is `null`:**
- ❌ **You are NOT logged in**
- **Solution:** Login first before accessing POS

---

### **Step 2: Login as Staff User**

```javascript
fetch('https://api.marinapizzas.com.au/graphql/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  credentials: 'include',
  body: JSON.stringify({
    query: `mutation {
      login(input: {
        username: "cashier1"
        password: "password123"
      }) {
        success
        user {
          id
          username
          role
          isStaffMember
        }
      }
    }`
  })
})
.then(r => r.json())
.then(data => {
  console.log('Login result:', data);
  if (data.data.login.success) {
    console.log('✅ Login successful!');
    // Now try POS query again
  }
});
```

---

### **Step 3: Check Network Tab for Actual Error**

1. Open **DevTools** (F12)
2. Go to **Network** tab
3. Find the failed request to `/graphql/`
4. Click on it
5. Go to **Response** tab
6. Look for the actual GraphQL error message

**Common error messages:**

#### Error 1: "Permission denied. Staff access required for POS."
```json
{
  "errors": [
    {
      "message": "Permission denied. Staff access required for POS."
    }
  ]
}
```
**Solution:** User needs `role: "staff"` or `role: "admin"`

#### Error 2: "Authentication required"
```json
{
  "errors": [
    {
      "message": "Authentication required"
    }
  ]
}
```
**Solution:** User is not logged in - need to login first

#### Error 3: Query syntax error
```json
{
  "errors": [
    {
      "message": "Cannot query field \"posProducts\" on type \"Query\"."
    }
  ]
}
```
**Solution:** Check query field name (should be `posProducts` not `pos_products`)

---

### **Step 4: Verify GraphQL Client Configuration**

Make sure your Apollo Client is configured correctly:

```javascript
import { ApolloClient, InMemoryCache, createHttpLink } from '@apollo/client';

const httpLink = createHttpLink({
  uri: 'https://api.marinapizzas.com.au/graphql/',
  credentials: 'include', // ← CRITICAL: Must include this!
});

const client = new ApolloClient({
  link: httpLink,
  cache: new InMemoryCache(),
  credentials: 'include', // ← Also set here
});
```

**Without `credentials: 'include'`, session cookies won't be sent!**

---

### **Step 5: Test POS Query Directly**

After logging in, test the query:

```javascript
fetch('https://api.marinapizzas.com.au/graphql/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  credentials: 'include',
  body: JSON.stringify({
    query: `query {
      posProducts {
        id
        name
        basePrice
        currentPrice
        barcode
        isInStock
      }
    }`
  })
})
.then(r => r.json())
.then(data => {
  console.log('POS Products:', data);
  if (data.errors) {
    console.error('❌ GraphQL Errors:', data.errors);
  } else {
    console.log('✅ Success! Products:', data.data.posProducts);
  }
});
```

---

## 🔍 Most Common Issues

### Issue 1: Not Logged In (90% of cases)

**Symptoms:**
- 400 Bad Request
- `data.me` returns `null`

**Fix:**
1. Login first using the `login` mutation
2. Make sure `credentials: 'include'` is set
3. Verify session cookie is being sent

### Issue 2: User Doesn't Have Staff Role

**Symptoms:**
- Error: "Permission denied. Staff access required for POS."

**Fix:**
1. Check user role: `query { me { role } }`
2. If `role: "customer"`, user needs to be updated to `role: "staff"`
3. Only admins can create staff users

### Issue 3: GraphQL Client Not Sending Cookies

**Symptoms:**
- Login works but queries fail
- Cookies not visible in Network tab

**Fix:**
1. Add `credentials: 'include'` to Apollo Client
2. Check CORS settings on backend
3. Verify cookies are being set after login

### Issue 4: Query Field Name Wrong

**Symptoms:**
- Error: "Cannot query field..."

**Fix:**
- Use `posProducts` (camelCase) not `pos_products` (snake_case)
- GraphQL automatically converts, but check your query

---

## 📋 Complete Debugging Checklist

- [ ] User is logged in (`me` query returns user data)
- [ ] User has `role: "staff"` or `role: "admin"`
- [ ] GraphQL client has `credentials: 'include'`
- [ ] Session cookie is visible in Network tab
- [ ] Query uses correct field names (`posProducts` not `pos_products`)
- [ ] Query syntax is correct
- [ ] No CORS errors in console
- [ ] Backend server is running and accessible

---

## 🚀 Quick Test Script

Copy and paste this in browser console to test everything:

```javascript
// Test 1: Check if logged in
async function testPOSAccess() {
  console.log('🔍 Testing POS Access...\n');
  
  // Step 1: Check current user
  const meResponse = await fetch('https://api.marinapizzas.com.au/graphql/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({
      query: `query { me { id username role isStaffMember isAdmin } }`
    })
  });
  
  const meData = await meResponse.json();
  console.log('1. Current User:', meData.data.me);
  
  if (!meData.data.me) {
    console.error('❌ NOT LOGGED IN - Please login first!');
    return;
  }
  
  if (!meData.data.me.isStaffMember && !meData.data.me.isAdmin) {
    console.error('❌ User does not have staff access!');
    console.log('User role:', meData.data.me.role);
    return;
  }
  
  console.log('✅ User has access\n');
  
  // Step 2: Test POS query
  const posResponse = await fetch('https://api.marinapizzas.com.au/graphql/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({
      query: `query { posProducts { id name basePrice } }`
    })
  });
  
  const posData = await posResponse.json();
  console.log('2. POS Products Response:', posData);
  
  if (posData.errors) {
    console.error('❌ GraphQL Errors:', posData.errors);
  } else {
    console.log('✅ POS Query Successful!');
    console.log('Products found:', posData.data.posProducts.length);
  }
}

// Run the test
testPOSAccess();
```

---

## 💡 If Still Not Working

1. **Check the actual error message** in Network tab → Response
2. **Verify backend is running** - test endpoint directly
3. **Check server logs** on droplet for detailed errors
4. **Test in GraphiQL** at `https://api.marinapizzas.com.au/graphql/`

---

**Most likely fix: Login first, then make sure `credentials: 'include'` is set in your GraphQL client!**
