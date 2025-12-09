# OTP Email Authentication Implementation

## Overview

The TRACE-MUSIC AuthService now includes secure email-based OTP (One-Time Password) authentication. This document describes the implementation, usage, and configuration.

## Architecture

The OTP authentication flow involves four main components:

1. **Frontend/Client**: Calls login and verify-otp REST endpoints
2. **Backend REST Gateway** (`backend/api.py`): Proxies requests to AuthService
3. **AuthService gRPC Server** (`AuthService/cloud.py`): Handles authentication logic
4. **Email Utility** (`AuthService/utils.py`): Generates and sends OTP via Gmail SMTP

## Authentication Flow

```
User Registration
    ↓
User Login (username + password)
    ↓ [Backend validates]
    ↓ [AuthService checks credentials]
    ↓ [If valid: generate 6-digit OTP]
    ↓ [Send OTP to user's email]
    ↓ [Store OTP server-side with 5-min expiration]
OTP Email Received by User
    ↓
User Submits OTP Code
    ↓ [Backend/AuthService verifies OTP]
    ↓ [If valid: delete stored OTP]
    ↓ [Issue authentication token]
Authentication Successful
```

## Key Implementation Details

### OTP Generation (`utils.py`)

- **Function**: `generate_otp()`
- **Output**: 6-digit random numeric string (e.g., `"123456"`)
- **Used in**: Login flow after credential validation

### OTP Storage (`cloud.py`)

- **Structure**: `pending_otp` dictionary in `UserServiceSkeleton`
- **Key**: Username
- **Value**: Object containing:
  - `pending_id`: UUID that matches the login response (prevents CSRF)
  - `otp_code`: The 6-digit code sent to user's email
  - `email`: User's email address (for reference)
  - `expires_at`: Unix timestamp (current_time + 300 seconds)

### OTP Transmission (`utils.py`)

- **Function**: `send_otp(to_email, otp_code=None)`
- **SMTP Server**: Gmail (`smtp.gmail.com:587`)
- **Authentication**: 
  - `from_email`: Gmail address (from `AuthService/params.py`)
  - `app_password`: Gmail App Password (for 2FA accounts)
- **Environment Variables** (optional override):
  - `CLOUD_EMAIL_FROM`
  - `CLOUD_EMAIL_PASS`

### OTP Verification (`cloud.py`)

- **Method**: `VerifyOtp(login, pending_id, otp_code)`
- **Checks**:
  1. Pending OTP entry exists for user
  2. `pending_id` matches stored value
  3. OTP has not expired
  4. Supplied `otp_code` matches stored code
- **Success**: Delete OTP entry, issue authentication token
- **Failure**: Return empty token

## REST API Endpoints

### Register User
```
POST /auth/register
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "secure_password",
  "quota_gb": 1
}

Response:
{
  "ok": true,
  "message": "Account created successfully! You have 1GB free storage.",
  "username": "john_doe",
  "quota_gb": 1
}
```

### Login (Request OTP)
```
POST /auth/login
Content-Type: application/json

{
  "username": "john_doe",
  "password": "secure_password"
}

Response:
{
  "ok": true,
  "message": "OTP sent to your email. Please verify to complete login.",
  "pending_id": "uuid-here",
  "username": "john_doe"
}
```

### Verify OTP (Complete Login)
```
POST /auth/verify-otp
Content-Type: application/json

{
  "username": "john_doe",
  "pending_id": "uuid-from-login",
  "otp": "123456"
}

Response on Success:
{
  "ok": true,
  "message": "Login successful!",
  "token": "authentication-token-uuid",
  "username": "john_doe"
}

Response on Failure:
{
  "ok": false,
  "detail": "Invalid or expired OTP"
}
```

## Configuration

### Gmail Setup (for sending OTPs)

1. Enable 2-Factor Authentication on your Gmail account
2. Generate an App Password:
   - Go to https://myaccount.google.com/apppasswords
   - Select "Mail" and "Windows Computer"
   - Copy the 16-character password

3. Update `AuthService/params.py`:
   ```python
   from_email = "your-email@gmail.com"
   app_password = "your-16-char-app-password"
   ```

   OR set environment variables before starting AuthService:
   ```powershell
   $env:CLOUD_EMAIL_FROM = "your-email@gmail.com"
   $env:CLOUD_EMAIL_PASS = "your-16-char-app-password"
   
   # Then start AuthService
   ./start_authservice.ps1
   ```

### OTP Expiration

- Default: **5 minutes** (300 seconds)
- Location: `AuthService/cloud.py` in `Login()` method
- To adjust: Change the `time.time() + 300` value

## Testing

### Unit Tests

Run OTP-specific tests:
```powershell
python -m pytest CloudSim/tests/test_otp_auth.py -v
```

Tests include:
- OTP generation (6-digit numeric codes)
- Password hashing and verification
- OTP storage and expiration logic

### Manual Testing

1. **Start the system**:
   ```powershell
   .\start_all.ps1
   ```

2. **Register a user** with a valid email address you control

3. **Login** with the registered credentials

4. **Check your email** for the OTP code

5. **Submit the OTP** to verify login

6. **Receive authentication token** on success

## Security Considerations

- ✅ Passwords are hashed using bcrypt (salted)
- ✅ OTPs are 6-digit random codes (1 in 1,000,000 probability)
- ✅ OTPs expire after 5 minutes
- ✅ OTP verification requires `pending_id` (prevents replay attacks)
- ✅ Each login generates a unique OTP (no reuse)
- ⚠️ Email is sent over TLS (encrypted in transit)
- ⚠️ App passwords should not be committed to version control

## Future Improvements

- Rate limiting on login attempts
- Account lockout after N failed OTP attempts
- SMS as fallback OTP delivery method
- Remember device (skip OTP on trusted devices)
- Audit logging of login events
- Two-factor authentication (TOTP/authenticator apps)

## Files Modified/Created

- **Modified**: `AuthService/cloud.py` — Enhanced Login and VerifyOtp methods
- **Modified**: `AuthService/utils.py` — Updated send_otp to accept OTP parameter
- **Modified**: `CONTRIBUTING.md` — Added OTP authentication documentation
- **Created**: `CloudSim/tests/test_otp_auth.py` — Unit tests for OTP logic
