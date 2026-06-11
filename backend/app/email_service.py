import httpx
from app.config import settings

def get_access_token() -> str:
    response = httpx.post(
        "https://oauth2.googleapis.com/token",
        data={
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "refresh_token": settings.GMAIL_REFRESH_TOKEN,
            "grant_type": "refresh_token",
        }
    )
    data = response.json()
    if "access_token" not in data:
        raise Exception(f"Google token error: {data}")
    return data["access_token"]

def send_email(to: str, subject: str, html: str):
    access_token = get_access_token()
    
    import base64
    from email.mime.text import MIMEText
    
    message = MIMEText(html, "html")
    message["to"] = to
    message["from"] = settings.GMAIL_USER
    message["subject"] = subject
    
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    
    httpx.post(
        f"https://gmail.googleapis.com/gmail/v1/users/me/messages/send",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"raw": raw}
    )

def send_otp_email(email: str, otp: str):
    send_email(
        to=email,
        subject="Verify your email",
        html=f"""
        <h2>Email Verification</h2>
        <p>Your OTP is:</p>
        <h1 style="color: #6E40C9; letter-spacing: 8px;">{otp}</h1>
        <p>This OTP will expire in 10 minutes.</p>
        <p>If you didn't request this, ignore this email.</p>
        """
    )

def send_password_reset_email(email: str, otp: str):
    send_email(
        to=email,
        subject="Password Reset OTP",
        html=f"""
        <h2>Password Reset</h2>
        <p>Your OTP for password reset is:</p>
        <h1 style="color: #E53E3E; letter-spacing: 8px;">{otp}</h1>
        <p>This OTP will expire in 10 minutes.</p>
        <p>If you didn't request this, please secure your account immediately.</p>
        """
    )