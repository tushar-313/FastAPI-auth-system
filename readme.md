# 🔐 FastAPI Auth API

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-black?style=for-the-badge&logo=JSON%20web%20tokens)

A production-ready authentication REST API built with FastAPI and PostgreSQL.

## 🌐 Live Demo

https://fastapi-auth-system-btg6.onrender.com/docs

## ✨ Features

- 📧 **Register** — Email + password registration with bcrypt hashing
- ✅ **Email OTP Verification** — 6-digit OTP via Gmail API, 10 min expiry
- 🔑 **Login** — JWT access + refresh tokens stored in HttpOnly cookies
- 🔄 **Refresh Token** — Automatic token rotation for security
- 🔒 **Forgot Password** — OTP-based password reset via email
- 🚪 **Logout** — Secure cookie clearance
- 🌐 **Google OAuth** — Login with Google
- 👤 **Protected Routes** — JWT verification via HttpOnly cookies

## 🔒 Security

- Passwords hashed with **bcrypt**
- Tokens stored in **HttpOnly cookies** — XSS safe
- **SameSite=Strict** — CSRF protection
- **Secure flag** — HTTPS only in production
- OTP expires in **10 minutes**
- **Token rotation** on every refresh
- Gmail API with OAuth 2.0 — no plain passwords

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI, Python 3.11 |
| Database | PostgreSQL 16 |
| ORM | SQLAlchemy + Alembic |
| Auth | JWT (python-jose) + bcrypt |
| Email | Gmail API (OAuth 2.0) |
| Container | Docker + Docker Compose |
| Deployment | Render |

## 📁 Project Structure

    backend/
    ├── app/
    │   ├── main.py
    │   ├── config.py
    │   ├── database.py
    │   ├── models.py
    │   ├── schemas.py
    │   ├── dependencies.py
    │   ├── jwt_handler.py
    │   ├── email_service.py
    │   └── routers/
    │       └── auth.py
    ├── alembic/
    ├── Dockerfile
    ├── docker-compose.yml
    └── requirements.txt

## 🚀 Run Locally

**Prerequisites:** Docker Desktop installed

**1. Clone the repo:**

    git clone https://github.com/tushar-313/FastAPI-auth-system
    cd FastAPI-auth-system

**2. Create .env file in backend/:**

    DATABASE_URL=postgresql://postgres:postgres123@postgres:5432/authproject
    SECRET_KEY=your-secret-key
    ALGORITHM=HS256
    ACCESS_TOKEN_EXPIRE_MINUTES=30
    REFRESH_TOKEN_EXPIRE_DAYS=7
    GMAIL_USER=your-gmail@gmail.com
    GMAIL_REFRESH_TOKEN=your-refresh-token
    GOOGLE_CLIENT_ID=your-google-client-id
    GOOGLE_CLIENT_SECRET=your-google-client-secret
    GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback


**3. Start with Docker:**

    docker compose up --build

**4. Run migrations:**

    docker compose exec backend alembic upgrade head

**5. Open API docs:**

    http://localhost:8000/docs

## 📡 API Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/register` | Register new user | ❌ |
| POST | `/auth/verify-otp` | Verify email OTP | ❌ |
| POST | `/auth/login` | Login user | ❌ |
| POST | `/auth/refresh-token` | Refresh access token | ❌ |
| POST | `/auth/logout` | Logout user | ❌ |
| POST | `/auth/forgot-password` | Send reset OTP | ❌ |
| POST | `/auth/reset-password` | Reset password | ❌ |
| GET | `/auth/google/login` | Google OAuth login | ❌ |
| GET | `/auth/google/callback` | Google OAuth callback | ❌ |
| GET | `/auth/me` | Get current user | ✅ |
| GET | `/health` | Health check | ❌ |

## 🌍 Environment Variables

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `SECRET_KEY` | JWT signing secret |
| `ALGORITHM` | JWT algorithm (HS256) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token expiry |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token expiry |
| `GMAIL_USER` | Gmail address for sending emails |
| `GMAIL_REFRESH_TOKEN` | Gmail OAuth 2.0 refresh token |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret |
| `GOOGLE_REDIRECT_URI` | Google OAuth redirect URI |
