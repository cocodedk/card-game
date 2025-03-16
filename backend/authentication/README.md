# Authentication System

This module provides authentication functionality for the Idiot Card Game application.

## Features

- User registration
- User login
- User logout
- Password change
- JWT token-based authentication
- User profile management
- Neo4j-based token blacklisting

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
- Passwords are securely hashed using Django's password hashing
- User data is stored in Neo4j database

## Token Blacklisting

This application implements a Neo4j-based token blacklisting system for enhanced security. When a user logs out, their refresh token is added to a blacklist to prevent its reuse, even if it hasn't expired yet.

### How Token Blacklisting Works

1. **Storage**: Blacklisted tokens are stored in Neo4j using the `BlacklistedToken` model
2. **Validation**: Every token is checked against the blacklist during authentication
3. **Logout Process**: When a user logs out, their refresh token is decoded and added to the blacklist
4. **Expiration**: Blacklisted tokens include their original expiration time to allow for cleanup

### BlacklistedToken Model

```python
class BlacklistedToken(StructuredNode):
    uid = StringProperty(unique_index=True, default=lambda: str(uuid.uuid4()))
    token = StringProperty(unique_index=True)  # The actual token string
    user_uid = StringProperty(index=True)  # UID of the user who owned this token
    blacklisted_at = DateTimeProperty(default_now=True)
    expires_at = DateTimeProperty()  # When the token would have expired
```

### Token Validation

During authentication, the JWT authentication backend checks if the token is blacklisted:

```python
def get_validated_token(self, raw_token):
    # First validate the token using the parent method
    validated_token = super().get_validated_token(raw_token)

    # Check if the token is blacklisted
    if BlacklistedToken.is_blacklisted(str(raw_token)):
        raise InvalidToken('Token is blacklisted')

    return validated_token
```

### Cleanup Process

To prevent the blacklist from growing indefinitely, a cleanup method is provided:

```python
@classmethod
def cleanup_expired(cls):
    """Remove expired tokens from the blacklist"""
    now = datetime.now()
    # Find all expired tokens
    expired_tokens = cls.nodes.filter(expires_at__lt=now)
    # Delete them
    for token in expired_tokens:
        token.delete()
    return len(expired_tokens)
```

This method should be called periodically (e.g., via a scheduled task) to remove tokens that have already expired.

### Benefits of Neo4j-Based Blacklisting

- **Consistency**: All application data is stored in Neo4j, eliminating the need for a separate database
- **Persistence**: Blacklisted tokens remain in the database even if the server restarts
- **Performance**: Neo4j's indexing allows for fast token lookups
- **Scalability**: The solution scales well with the number of users and tokens
