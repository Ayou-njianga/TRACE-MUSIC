# Contributing to TRACE-MUSIC

Thank you for your interest in contributing to TRACE-MUSIC. This document explains how to contribute, run tests, and what to expect for PRs.

- Fork the repository and create a topic branch for your work.
- Keep changes focused and split large work into multiple PRs.
- Write tests for new functionality and ensure all existing tests pass.
- Follow the existing project style and naming conventions.
- Open a pull request describing the change, the motivation, and any migration or upgrade steps.

Testing
- Install development dependencies (recommended inside a virtual environment):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r CloudSim/requirements.txt
pip install pytest
pytest CloudSim/tests
```

Code Review
- The PR should include:
  - What changed and why
  - How to run the code locally
  - Any performance or security considerations

Security
- Do not commit sensitive information (passwords, API keys, private certs).
- If you discover a security issue, open a private issue and mark it as security.

License
- By contributing, you agree to license your contribution under the project license specified in the repository (add `LICENSE` file if not present).

## OTP Email Authentication

The project includes email-based OTP (One-Time Password) authentication for secure user login. This feature is implemented in the AuthService:

### How it works:

1. **User Registration** (`POST /auth/register`): Users provide username, email, and password.
2. **Login Attempt** (`POST /auth/login`): User provides credentials.
3. **OTP Generation**: AuthService generates a 6-digit OTP code and stores it server-side with a 5-minute expiration.
4. **Email Delivery**: The OTP is sent to the user's registered email address via Gmail SMTP.
5. **OTP Verification** (`POST /auth/verify-otp`): User submits the OTP code they received. If valid, an authentication token is issued.

### Email Configuration:

Email credentials are stored in `AuthService/params.py`:
- `from_email`: The Gmail address that sends OTP emails
- `app_password`: Gmail App Password (for 2FA-enabled accounts)

Alternatively, set environment variables:
```
CLOUD_EMAIL_FROM=your-email@gmail.com
CLOUD_EMAIL_PASS=your-app-password
```

### Key Files:

- `AuthService/cloud.py`: Main AuthService gRPC server with Login and VerifyOtp methods
- `AuthService/utils.py`: OTP generation and email sending logic
- `AuthService/params.py`: Email configuration
- `backend/api.py`: REST endpoints for register, login, and verify-otp (proxy to AuthService)

### Testing OTP Flow:

1. Register a user via `POST /auth/register` with a valid email
2. Login via `POST /auth/login` with the credentials
3. Check the registered email inbox for the OTP code
4. Submit the OTP via `POST /auth/verify-otp` with the login, pending_id, and otp code
5. Receive an authentication token on success
