# Authentication System

This module provides authentication functionality for the Idiot Card Game application.

## Features

- User registration
- User login
- User logout
- Password change
- JWT token-based authentication
- User profile management

## API Endpoints

### Registration

```
POST /api/auth/register/
```

**Request Body:**
```json
{
  "username": "your_username",
  "email": "your_email@example.com",
  "password": "your_password",
  "confirm_password": "your_password",
  "first_name": "Your",
  "last_name": "Name"
}
```

**Response:**
```json
{
  "user": {
    "uid": "user_uid",
    "username": "your_username",
    "email": "your_email@example.com",
    "first_name": "Your",
    "last_name": "Name"
  },
  "tokens": {
    "access": "access_token",
    "refresh": "refresh_token"
  },
  "message": "User registered successfully"
}
```

### Login

```
POST /api/auth/login/
```

**Request Body:**
```json
{
  "username": "your_username",
  "password": "your_password"
}
```

**Response:**
```json
{
  "user": {
    "uid": "user_uid",
    "username": "your_username",
    "email": "your_email@example.com",
    "first_name": "Your",
    "last_name": "Name"
  },
  "tokens": {
    "access": "access_token",
    "refresh": "refresh_token"
  }
}
```

### Logout

```
POST /api/auth/logout/
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "refresh": "refresh_token"
}
```

**Response:**
```json
{
  "message": "Logout successful"
}
```

### Change Password

```
POST /api/auth/change-password/
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "current_password": "your_current_password",
  "new_password": "your_new_password",
  "confirm_new_password": "your_new_password"
}
```

**Response:**
```json
{
  "message": "Password changed successfully"
}
```

### Get Current User

```
GET /api/auth/me/
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "uid": "user_uid",
  "username": "your_username",
  "email": "your_email@example.com",
  "first_name": "Your",
  "last_name": "Name"
}
```

### Update User Profile

```
PUT /api/auth/profile/
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "first_name": "Updated",
  "last_name": "Name"
}
```

**Response:**
```json
{
  "uid": "user_uid",
  "username": "your_username",
  "email": "your_email@example.com",
  "first_name": "Updated",
  "last_name": "Name",
  "created_at": "2023-01-01T00:00:00Z"
}
```

## Testing

To run the authentication tests:

```bash
cd /app
python backend/authentication/run_tests.py
```

For manual testing, you can use the test script:

```bash
cd /app
python backend/authentication/test_auth.py
```

## Implementation Details

- Uses JWT (JSON Web Tokens) for authentication
- Tokens are stored in the client side (no server-side sessions)
- Access tokens expire after a short period (typically 5 minutes)
- Refresh tokens can be used to obtain new access tokens
- Refresh tokens are blacklisted on logout for security
- Passwords are securely hashed using Django's password hashing
- User data is stored in Neo4j database
