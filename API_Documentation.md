# LegalCodex HTTP API Documentation

## Overview

The LegalCodex HTTP API provides programmatic access to legal document processing and analysis through a RESTful interface. The API is built with FastAPI and supports session-based authentication via HTTP cookies.

**API Version:** v1
**Base URL:** `http://localhost:8000/api/v1` (default local deployment)

---

## Authentication

The API uses cookie-based session authentication with HTTP-only cookies. All protected endpoints require a valid `lc_access` session cookie.

### Authentication Flow

1. **Login:** Submit credentials via `POST /api/v1/auth/login`
2. **Session established:** Server sets an `lc_access` HTTP-only cookie with path `/api/v1`
3. **Access protected resources:** Include the cookie in subsequent requests (automatic in browsers; explicit in API clients)
4. **Logout:** Call `POST /api/v1/auth/logout` to clear the session cookie

### Cookie Details

- **Name:** `lc_access`
- **Value:** `GRANTED` (on successful authentication)
- **Flags:** `HttpOnly`, `SameSite=lax`
- **Path:** `/api/v1`
- **Max-Age:** Session-based (cleared on logout)

---

## Endpoints

### Authentication Routes

#### POST `/api/v1/auth/login`

Authenticate a user and establish a session.

**Request**

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "string",
  "password": "string"
}
```

**Parameters**

| Field      | Type   | Required | Description       |
|-----------|--------|----------|-------------------|
| `username` | string | Yes      | User identifier   |
| `password` | string | Yes      | User password     |

**Response**

- **Status:** `204 No Content`
- **Headers:** `Set-Cookie: lc_access=GRANTED; HttpOnly; SameSite=lax; Path=/api/v1`

**Error Responses**

| Status | Condition                         |
|--------|-----------------------------------|
| 401    | Invalid username or password      |

**Examples**

```bash
# Using curl
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "sauvp", "password": "hello"}' \
  -c cookies.txt
```

```javascript
// Using fetch (JavaScript)
const response = await fetch('/api/v1/auth/login', {
  method: 'POST',
  credentials: 'include',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username: 'sauvp', password: 'hello' })
});

if (response.status === 204) {
  console.log('Login successful');
}
```

```python
# Using requests (Python)
import requests

response = requests.post(
    'http://localhost:8000/api/v1/auth/login',
    json={'username': 'sauvp', 'password': 'hello'},
    cookies={}
)

if response.status_code == 204:
    print('Login successful')
```

---

#### POST `/api/v1/auth/logout`

Clear the session and revoke authentication.

**Request**

```http
POST /api/v1/auth/logout
```

**Response**

- **Status:** `204 No Content`
- **Headers:** `Set-Cookie: lc_access=; Max-Age=0; Path=/api/v1`

**Examples**

```bash
curl -X POST http://localhost:8000/api/v1/auth/logout -b cookies.txt
```

```javascript
const response = await fetch('/api/v1/auth/logout', {
  method: 'POST',
  credentials: 'include'
});
```

---

#### GET `/api/v1/auth/session`

Check the current authentication status.

**Request**

```http
GET /api/v1/auth/session
```

**Response**

**Success (Authenticated)**

- **Status:** `200 OK`
- **Body:**
  ```json
  {
    "authenticated": true
  }
  ```

**Unauthenticated**

- **Status:** `401 Unauthorized`
- **Body:**
  ```json
  {
    "authenticated": false
  }
  ```

**Examples**

```bash
curl -X GET http://localhost:8000/api/v1/auth/session -b cookies.txt
```

```javascript
const response = await fetch('/api/v1/auth/session', {
  method: 'GET',
  credentials: 'include'
});

const data = await response.json();
console.log('Authenticated:', data.authenticated);
```

---

### Status Routes

#### GET `/api/v1/status`

Retrieve the server status and health information.

**Request**

```http
GET /api/v1/status
```

**Response**

- **Status:** `200 OK`
- **Body:**
  ```json
  {
    "status": "ok",
    "message": "LegalCodex HTTP API server is running",
    "cwd": "/current/working/directory",
    "timestamp_utc": "2026-02-21T14:30:45.123456Z"
  }
  ```

**Response Fields**

| Field          | Type   | Description                                 |
|---------------|--------|---------------------------------------------|
| `status`      | string | Status indicator (`ok`)                     |
| `message`     | string | Human-readable status message               |
| `cwd`         | string | Current working directory of the server     |
| `timestamp_utc` | string | ISO 8601 UTC timestamp (Z suffix)          |

**Examples**

```bash
curl -X GET http://localhost:8000/api/v1/status
```

```javascript
const response = await fetch('/api/v1/status');
const data = await response.json();
console.log('Server status:', data.status);
console.log('Timestamp:', data.timestamp_utc);
```

---

## Data Types

### LoginRequest

```json
{
  "username": "string",
  "password": "string"
}
```

### AuthSessionResponse

```json
{
  "authenticated": "boolean"
}
```

### StatusResponse

```json
{
  "status": "string",
  "message": "string",
  "cwd": "string",
  "timestamp_utc": "string (ISO 8601)"
}
```

---

## HTTP Status Codes

| Code | Meaning                                        | Usage                                    |
|------|------------------------------------------------|------------------------------------------|
| 200  | OK                                             | Successful request with response body    |
| 204  | No Content                                     | Successful request without response body |
| 401  | Unauthorized                                   | Invalid credentials or missing session   |
| 404  | Not Found                                      | Invalid endpoint path                    |
| 500  | Internal Server Error                          | Server error condition                   |

---

## Error Handling

### Error Response Format

When an error occurs (4xx/5xx status), the response body contains:

```json
{
  "detail": "Human-readable error message"
}
```

### Common Error Scenarios

**Invalid Credentials**

```
Status: 401 Unauthorized
{
  "detail": "Unauthorized"
}
```

**Missing Session**

```
Status: 401 Unauthorized
{
  "detail": "Unauthorized"
}
```

**Invalid Endpoint**

```
Status: 404 Not Found
{
  "detail": "Not Found"
}
```

---

## Best Practices

### 1. Session Management

- Always use `credentials: 'include'` in browser fetch requests to send cookies automatically
- API clients (curl, requests, etc.) should preserve cookies across requests using cookie jars
- Session cookies have no explicit expiration; they are cleared only via logout or server restart

### 2. Error Handling

- Check HTTP status codes to determine success or failure
- Implement retry logic for 500 errors with exponential backoff
- Never log or store user credentials

### 3. Security

- Always use HTTPS in production deployments
- The `lc_access` cookie is HTTP-only and cannot be accessed from JavaScript
- All authentication data is validated server-side

### 4. API Clients

**Python - requests library**

```python
import requests

session = requests.Session()

# Login
response = session.post(
    'http://localhost:8000/api/v1/auth/login',
    json={'username': 'user', 'password': 'pass'}
)
assert response.status_code == 204

# Cookies are automatically managed by the session

# Check session
response = session.get('http://localhost:8000/api/v1/auth/session')
data = response.json()
print(f"Authenticated: {data['authenticated']}")

# Logout
response = session.post('http://localhost:8000/api/v1/auth/logout')
assert response.status_code == 204
```

**JavaScript/Node.js - fetch API**

```javascript
// Login
const loginRes = await fetch('/api/v1/auth/login', {
  method: 'POST',
  credentials: 'include',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username: 'user', password: 'pass' })
});
console.assert(loginRes.status === 204);

// Session check
const sessionRes = await fetch('/api/v1/auth/session', {
  method: 'GET',
  credentials: 'include'
});
const data = await sessionRes.json();
console.log(`Authenticated: ${data.authenticated}`);

// Logout
const logoutRes = await fetch('/api/v1/auth/logout', {
  method: 'POST',
  credentials: 'include'
});
console.assert(logoutRes.status === 204);
```

---

## Deployment Considerations

- The API serves the frontend from `/` (index.html) and static assets from `/`, `/styles.css`, `/js/auth-app.js`, etc.
- Static assets are served with correct MIME types (JavaScript files use `application/javascript`)
- API routes are prefixed with `/api/v1` to allow future API versioning
- The server includes request logging and can be configured with `--verbose` flag for debug output

---

## Support & Feedback

For issues, feature requests, or documentation improvements, please refer to the project repository and issue tracker.
