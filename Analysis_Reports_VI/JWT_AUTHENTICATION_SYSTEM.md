# JWT Authentication System - Hệ thống Xác Thực

## 📋 Tổng Quan
Hệ thống sử dụng **JWT (JSON Web Token)** để xác thực người dùng. Mỗi khi đăng nhập thành công, server trả về 1 token, frontend lưu trong `localStorage` và gửi kèm mỗi request tới backend.

---

## 🔐 1. BACKEND - API Authentication Endpoints

### File chính: [backend/api/auth.py](../backend/api/auth.py)

#### **1.1 POST /api/auth/login** - Đăng Nhập
```python
Endpoint: POST /api/auth/login
Request JSON:
{
  "username": "admin",
  "password": "admin123"
}

Response Success (200):
{
  "message": "Login successful",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "username": "admin",
    "full_name": "Administrator",
    "email": "admin@parking.com",
    "role": "admin"
  }
}

Response Error:
- 400: Username and password are required
- 401: Invalid username or password
- 403: User account is inactive
```

**Xử lý Password:**
- Hỗ trợ cả **Bcrypt** và **Werkzeug** password hashing
- Kiểm tra password theo định dạng hash (nếu bắt đầu với `$2` → dùng Bcrypt, ngược lại → Werkzeug)

**Login History Recording:**
- Ghi lại mỗi lần login (thành công/thất bại)
- Lưu: user_id, IP address, User-Agent, failure reason
- Dùng để audit và security tracking

---

#### **1.2 POST /api/auth/register** - Đăng Ký Tài Khoản (Admin Only)
```python
Endpoint: POST /api/auth/register
Header: Authorization: Bearer <JWT_TOKEN>
Request JSON:
{
  "username": "user1",
  "password": "password123",
  "email": "user1@parking.com",
  "full_name": "User One",
  "role": "staff"  // or "admin"
}

Response Success (201):
{
  "message": "User registered successfully",
  "user": {
    "id": 2,
    "username": "user1",
    "email": "user1@parking.com",
    "full_name": "User One",
    "role": "staff"
  }
}

Response Error:
- 401: Token is missing / Invalid token
- 403: Admin access required
- 400: Username/Email already exists
```

**Yêu cầu:**
- Chỉ Admin mới có thể đăng ký tài khoản mới
- Username và Email phải duy nhất trong hệ thống

---

#### **1.3 POST /api/auth/logout** - Đăng Xuất
```python
Endpoint: POST /api/auth/logout
Header: Authorization: Bearer <JWT_TOKEN>

Response Success (200):
{
  "message": "Logout successful"
}

Response Error:
- 401: Token is missing / Invalid token
```

**Lưu ý:**
- Token bị vô hiệu hóa trên client side (xóa khỏi localStorage)
- Server không lưu blacklist token, không cần logout endpoint, nhưng có để consistency

---

#### **1.4 GET /api/auth/verify** - Kiểm Tra Token
```python
Endpoint: GET /api/auth/verify
Header: Authorization: Bearer <JWT_TOKEN>

Response Success (200):
{
  "message": "Token is valid",
  "user_id": 1,
  "role": "admin"
}

Response Error:
- 401: Token is missing / Expired / Invalid
```

**Dùng để:**
- Kiểm tra token có còn hợp lệ không
- Lấy user_id và role từ token

---

#### **1.5 GET /api/auth/users** - Lấy Danh Sách Users (Admin Only)
```python
Endpoint: GET /api/auth/users
Header: Authorization: Bearer <JWT_TOKEN>

Response Success (200):
{
  "message": "Users retrieved successfully",
  "users": [
    {
      "id": 1,
      "username": "admin",
      "email": "admin@parking.com",
      "full_name": "Administrator",
      "role": "admin",
      "is_active": true,
      "created_at": "2025-12-30T10:00:00"
    },
    ...
  ]
}

Response Error:
- 401: Token is missing / Invalid
- 403: Admin access required
```

---

#### **1.6 DELETE /api/auth/user/<user_id>** - Xóa User (Admin Only)
```python
Endpoint: DELETE /api/auth/user/<user_id>
Header: Authorization: Bearer <JWT_TOKEN>

Response Success (200):
{
  "message": "User {username} deleted successfully"
}

Response Error:
- 400: Cannot delete your own account
- 401: Token is missing / Invalid
- 403: Admin access required
- 404: User not found
```

---

## 🔑 2. JWT TOKEN STRUCTURE

### Token Generation (Backend)
```python
expiration_time = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
token = jwt.encode(
    {
        'sub': str(user.id),           # Subject (identity)
        'user_id': user.id,             # User ID
        'username': user.username,      # Username
        'role': user.role,              # User Role (admin/staff)
        'exp': expiration_time          # Expiration time
    },
    JWT_SECRET_KEY,
    algorithm='HS256'
)
```

### Configuration
| Config | Value | Mô Tả |
|--------|-------|-------|
| **JWT_SECRET_KEY** | `jwt-dev-secret-key` | Secret key để sign token (Dev), từ env trong Production |
| **JWT_EXPIRATION_HOURS** | 24 | Token hết hạn sau 24 giờ |
| **JWT_HEADER_TYPE** | Bearer | Cách sử dụng token trong header: `Bearer <TOKEN>` |

---

## 🛡️ 3. DECORATORS - Bảo Vệ API

### **@token_required**
```python
@token_required
def protected_endpoint(current_user_id, current_user_role):
    """Endpoint được bảo vệ - cần JWT token"""
    return jsonify({'user_id': current_user_id})
```

**Xử lý:**
1. Kiểm tra header `Authorization: Bearer <TOKEN>`
2. Decode token bằng `JWT_SECRET_KEY`
3. Nếu token hợp lệ → truyền `current_user_id` và `current_user_role` vào hàm
4. Nếu token hết hạn → return 401 "Token has expired"
5. Nếu token không hợp lệ → return 401 "Invalid token"

### **@admin_required**
```python
@token_required
@admin_required
def admin_only_endpoint(current_user_id, current_user_role):
    """Endpoint chỉ Admin mới dùng được"""
    return jsonify({'message': 'Admin access granted'})
```

**Yêu cầu:**
- User phải có role = "admin"
- Nếu không → return 403 "Admin access required"

---

## 💻 4. FRONTEND - Token Management

### File chính: [frontend/src/api.ts](../frontend/src/api.ts) & [frontend/src/components/LoginPage.tsx](../frontend/src/components/LoginPage.tsx)

#### **4.1 Login Function**
```typescript
// Method 1: Sử dụng parkingApi
const { token, user } = await parkingApi.login(username, password);

// Method 2: Direct fetch (LoginPage.tsx)
const response = await fetch('http://localhost:5000/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username, password })
});
const data = await response.json();

if (response.ok) {
  // Lưu token vào localStorage
  localStorage.setItem('authToken', data.token);
  localStorage.setItem('user', JSON.stringify(data.user));
  // Redirect tới dashboard
  navigate('/dashboard');
}
```

#### **4.2 Automatic Token Injection (Request Interceptor)**
```typescript
// Mỗi request sẽ tự động thêm token vào header
api.interceptors.request.use(request => {
  const token = localStorage.getItem('authToken');
  if (token) {
    request.headers.Authorization = `Bearer ${token}`;
  }
  return request;
});
```

#### **4.3 Logout Function**
```typescript
parkingApi.logout();

// Xóa token từ localStorage
localStorage.removeItem('authToken');
localStorage.removeItem('user');
```

#### **4.4 Check Authentication**
```typescript
// Kiểm tra user đã đăng nhập chưa
const isAuthenticated = parkingApi.isAuthenticated();

// Lấy thông tin user hiện tại
const user = parkingApi.getCurrentUser();
```

---

## 🛡️ 5. PROTECTED ROUTES

### File: [frontend/src/components/ProtectedRoute.tsx](../frontend/src/components/ProtectedRoute.tsx)

```tsx
<ProtectedRoute requiredRole="admin">
  <AdminPanel />
</ProtectedRoute>

<ProtectedRoute>
  <Dashboard />
</ProtectedRoute>
```

**Chức năng:**
1. Kiểm tra `isAuthenticated()` - nếu không → redirect `/login`
2. Kiểm tra role (nếu có `requiredRole`) - nếu không match → redirect `/dashboard`
3. Nếu hợp lệ → render component

---

## 🔍 6. AUTHENTICATION FLOW

### **Login Flow**
```
User nhập username/password
       ↓
LoginPage.tsx gửi POST /api/auth/login
       ↓
Backend kiểm tra password (bcrypt hoặc werkzeug)
       ↓
Nếu OK: Tạo JWT token (24h expiration)
        Ghi login history
        Return token + user info
       ↓
Frontend lưu token vào localStorage
        Redirect tới /dashboard
```

### **Protected Request Flow**
```
Frontend request tới API
       ↓
Request Interceptor tự động thêm header:
Authorization: Bearer <TOKEN_FROM_LOCALSTORAGE>
       ↓
Backend @token_required decorator kiểm tra token
       ↓
Nếu OK: Decode token, lấy user_id + role
        Pass vào endpoint handler
       ↓
Nếu fail (expired/invalid): Return 401 Unauthorized
```

### **Logout Flow**
```
User click Logout
       ↓
Frontend xóa token từ localStorage
       ↓
Redirect tới /login
       ↓
Protected routes sẽ detect không có token → redirect /login
```

---

## 📊 7. Database Models

### **User Model** ([backend/models/user.py](../backend/models/user.py))
```python
class User(db.Model):
    id              → Primary Key
    username        → Unique, indexed (max 80 chars)
    password_hash   → Hashed password (Bcrypt or Werkzeug)
    email           → Unique, indexed
    full_name       → Optional
    role            → "admin" or "staff"
    is_active       → Boolean (true/false)
    created_at      → Datetime
```

### **LoginHistory Model** ([backend/models/login_history.py](../backend/models/login_history.py))
```python
class LoginHistory(db.Model):
    id              → Primary Key
    user_id         → Foreign Key (User)
    username        → Username attempted
    ip_address      → Client IP
    user_agent      → Browser/Client info
    login_status    → "success" or "failed"
    failure_reason  → Reason nếu failed (e.g., "Invalid password")
    created_at      → Datetime
```

---

## ⚙️ 8. Configuration

### File: [backend/config/config.py](../backend/config/config.py)

```python
# JWT Secret Key (Dev)
JWT_SECRET_KEY = 'jwt-dev-secret-key'

# JWT Secret Key (Production) - từ environment variable
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')

# Token expiration
JWT_EXPIRATION_HOURS = 24

# Token location in request
JWT_TOKEN_LOCATION = ["headers"]
JWT_HEADER_NAME = "Authorization"
JWT_HEADER_TYPE = "Bearer"
```

**Production Setup:**
- Set environment variable: `JWT_SECRET_KEY=<strong-random-key>`
- Dùng lệnh: `export JWT_SECRET_KEY=<key>` (Linux/Mac) hoặc `set JWT_SECRET_KEY=<key>` (Windows)

---

## 🔒 9. Security Best Practices Sử Dụng

| Quy Tắc | Triển Khai | Status |
|---------|----------|--------|
| **Secure Password Hashing** | Bcrypt + salt | ✅ |
| **JWT Token Expiration** | 24 hours | ✅ |
| **HTTPS** | Chưa setup (Dev mode) | ⚠️ Cần cho Production |
| **Token in localStorage** | localStorage được dùng | ⚠️ Có risk XSS |
| **CORS** | Cấu hình trong backend | ✅ |
| **Authorization Header** | Bearer token | ✅ |
| **Role-based Access** | @admin_required | ✅ |
| **Login History Audit** | Ghi lại tất cả login attempts | ✅ |

---

## 🚨 10. Possible Issues & Fixes

### **Issue 1: Token Expired**
```
Error: 401 - Token has expired

Fix: User cần login lại
```

### **Issue 2: No Token in Request**
```
Error: 401 - Token is missing

Fix: Kiểm tra localStorage có authToken không
     Hoặc Request Interceptor không hoạt động
```

### **Issue 3: CORS Error**
```
Error: No 'Access-Control-Allow-Origin' header

Fix: Kiểm tra backend CORS configuration
```

### **Issue 4: Invalid Secret Key**
```
Error: 401 - Invalid token (signature doesn't match)

Fix: JWT_SECRET_KEY trên backend và frontend không match
     Hoặc token từ source khác
```

---

## 📝 11. Default Credentials (Development)

```
Username: admin
Password: admin123
Role: admin
```

⚠️ **CHANGE DEFAULT CREDENTIALS IN PRODUCTION!**

---

## 🔗 Related Files
- [backend/api/auth.py](../backend/api/auth.py) - Authentication endpoints
- [backend/models/user.py](../backend/models/user.py) - User model
- [backend/models/login_history.py](../backend/models/login_history.py) - Login audit
- [backend/config/config.py](../backend/config/config.py) - JWT configuration
- [frontend/src/api.ts](../frontend/src/api.ts) - API client with token injection
- [frontend/src/components/LoginPage.tsx](../frontend/src/components/LoginPage.tsx) - Login UI
- [frontend/src/components/ProtectedRoute.tsx](../frontend/src/components/ProtectedRoute.tsx) - Route protection
