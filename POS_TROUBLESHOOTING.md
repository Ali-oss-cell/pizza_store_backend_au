# POS 400 Bad Request Error - Troubleshooting Guide

## 🔴 Error: `POST https://api.marinapizzas.com.au/graphql/ 400 (Bad Request)`

This error occurs when the GraphQL request is malformed or there's an authentication issue.

---

## 🔍 Common Causes & Solutions

### **1. User Not Authenticated**

**Problem:** POS queries require staff/admin authentication. If the user isn't logged in, the request fails.

**Solution:**
1. Make sure the user is logged in before accessing POS
2. Check if the session cookie is being sent with requests
3. Verify the user has `role: "staff"` or `role: "admin"`

**Test Login:**
```graphql
mutation {
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
}
```

**Check Current User:**
```graphql
query {
  me {
    id
    username
    role
    isStaffMember
    isAdmin
  }
}
```

---

### **2. GraphQL Query Format Issue**

**Problem:** The query might be using wrong field names or structure.

**Correct POS Query:**
```graphql
query POSProducts($categoryId: ID, $search: String, $inStockOnly: Boolean) {
  posProducts(categoryId: $categoryId, search: $search, inStockOnly: $inStockOnly) {
    id
    name
    basePrice
    currentPrice
    barcode
    sku
    stockQuantity
    isInStock
    isLowStock
    category
    imageUrl
    trackInventory
  }
}
```

**Variables:**
```json
{
  "categoryId": null,
  "search": null,
  "inStockOnly": false
}
```

**Common Mistakes:**
- ❌ Using `pos_products` (snake_case) - Use `posProducts` (camelCase)
- ❌ Using `category_id` - Use `categoryId`
- ❌ Using `in_stock_only` - Use `inStockOnly`
- ❌ Missing required fields in response

---

### **3. CORS or Session Cookie Issue**

**Problem:** The browser might not be sending session cookies with the request.

**Solution:**
1. Make sure your GraphQL client is configured to send credentials:
   ```javascript
   // Apollo Client example
   const client = new ApolloClient({
     uri: 'https://api.marinapizzas.com.au/graphql/',
     credentials: 'include', // Important!
     fetchOptions: {
       credentials: 'include'
     }
   });
   ```

2. Check browser DevTools → Network tab:
   - Look for the GraphQL request
   - Check if cookies are being sent
   - Check the request headers

3. Verify CORS settings on the backend allow credentials

---

### **4. Request Format Issue**

**Problem:** The request body might not be properly formatted.

**Correct Request Format:**
```json
{
  "query": "query POSProducts { posProducts { id name } }",
  "variables": {}
}
```

**Check:**
- Content-Type header: `application/json`
- Request method: `POST`
- Request body is valid JSON

---

### **5. User Doesn't Have Staff Permissions**

**Problem:** The user exists but doesn't have the right role or permissions.

**Check User Permissions:**
```graphql
query {
  me {
    id
    username
    role
    isStaffMember
    isAdmin
    permissions
  }
}
```

**Required:**
- `role: "staff"` OR `role: "admin"`
- `isStaffMember: true` OR `isAdmin: true`

**Fix:** Update the user to have staff role:
```graphql
mutation {
  updateTeamMember(id: "5", input: {
    role: "staff"
  }) {
    success
    user {
      id
      role
    }
  }
}
```

---

## 🧪 Step-by-Step Debugging

### **Step 1: Test GraphQL Endpoint**

Open browser console and test:
```javascript
fetch('https://api.marinapizzas.com.au/graphql/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  credentials: 'include',
  body: JSON.stringify({
    query: `
      query {
        me {
          id
          username
          role
        }
      }
    `
  })
})
.then(r => r.json())
.then(data => console.log('Response:', data))
.catch(err => console.error('Error:', err));
```

**Expected Response:**
```json
{
  "data": {
    "me": {
      "id": "1",
      "username": "cashier1",
      "role": "staff"
    }
  }
}
```

**If you get `null` for `me`:**
- User is not logged in
- Session cookie not being sent
- Need to login first

---

### **Step 2: Test POS Query Directly**

```javascript
fetch('https://api.marinapizzas.com.au/graphql/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  credentials: 'include',
  body: JSON.stringify({
    query: `
      query {
        posProducts {
          id
          name
          basePrice
        }
      }
    `
  })
})
.then(r => r.json())
.then(data => {
  console.log('Response:', data);
  if (data.errors) {
    console.error('GraphQL Errors:', data.errors);
  }
})
.catch(err => console.error('Error:', err));
```

**Check the response:**
- If `data.errors` exists, read the error message
- Common errors:
  - `"Permission denied. Staff access required for POS."` → User not staff/admin
  - `"Authentication required"` → User not logged in
  - Syntax errors → Query format issue

---

### **Step 3: Check Browser Console**

Look for:
1. **Network Tab:**
   - Find the failed request
   - Check Status Code (should be 200 for GraphQL, even with errors)
   - Check Request Headers (should include cookies)
   - Check Response Body (should show GraphQL errors)

2. **Console Tab:**
   - Look for JavaScript errors
   - Look for GraphQL error messages

---

### **Step 4: Check Server Logs**

On your droplet:
```bash
# Check gunicorn logs
tail -f /var/www/pizza-store-backend/logs/gunicorn-error.log

# Or check systemd logs
journalctl -u gunicorn -f
```

Look for:
- GraphQL parsing errors
- Authentication errors
- Permission denied errors

---

## ✅ Quick Fixes

### **Fix 1: Ensure User is Logged In**

```javascript
// In your POS component
useEffect(() => {
  // Check if user is logged in
  const checkAuth = async () => {
    const { data } = await client.query({ query: ME_QUERY });
    if (!data.me) {
      // Redirect to login
      window.location.href = '/login';
    }
  };
  checkAuth();
}, []);
```

### **Fix 2: Configure Apollo Client Correctly**

```javascript
import { ApolloClient, InMemoryCache, createHttpLink } from '@apollo/client';
import { setContext } from '@apollo/client/link/context';

const httpLink = createHttpLink({
  uri: 'https://api.marinapizzas.com.au/graphql/',
  credentials: 'include', // Important for session cookies!
});

const client = new ApolloClient({
  link: httpLink,
  cache: new InMemoryCache(),
  credentials: 'include',
});
```

### **Fix 3: Handle Errors Properly**

```javascript
const { data, error, loading } = useQuery(POS_PRODUCTS_QUERY, {
  onError: (error) => {
    console.error('GraphQL Error:', error);
    if (error.message.includes('Permission denied')) {
      alert('You need to be logged in as staff to access POS');
      // Redirect to login
    }
  }
});
```

---

## 📋 Checklist

Before reporting the issue, check:

- [ ] User is logged in (test with `me` query)
- [ ] User has `role: "staff"` or `role: "admin"`
- [ ] GraphQL client is configured with `credentials: 'include'`
- [ ] Query uses camelCase field names (`posProducts`, not `pos_products`)
- [ ] Request includes `Content-Type: application/json` header
- [ ] Browser is sending session cookies (check Network tab)
- [ ] No CORS errors in console
- [ ] GraphQL endpoint URL is correct

---

## 🆘 Still Not Working?

1. **Check the actual error message** in the Network tab response
2. **Test the query in GraphiQL** at `https://api.marinapizzas.com.au/graphql/`
3. **Check server logs** for detailed error messages
4. **Verify user permissions** with the `me` query

---

## 📞 Common Error Messages

| Error Message | Cause | Solution |
|--------------|-------|----------|
| `400 Bad Request` | Malformed query or auth issue | Check query format, ensure logged in |
| `Permission denied. Staff access required` | User not staff/admin | Update user role or login as staff |
| `Authentication required` | Not logged in | Login first |
| `Cannot query field "posProducts"` | Query not in schema | Check field name (camelCase) |
| `Variable "$categoryId" is never used` | Unused variable | Remove from query or use it |

---

**Need more help? Check the server logs for detailed error messages!**
