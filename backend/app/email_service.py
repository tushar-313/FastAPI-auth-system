import resend
from app.config import settings

resend.api_key = settings.RESEND_API_KEY

def send_otp_email(email: str, otp: str):
    resend.Emails.send({
        "from": "onboarding@resend.dev",
        "to": email,
        "subject": "Verify your email",
        "html": f"""
        <h2>Email Verification</h2>
        <p>Your OTP is:</p>
        <h1 style="color: #6E40C9; letter-spacing: 8px;">{otp}</h1>
        <p>This OTP will expire in 10 minutes.</p>
        <p>If you didn't request this, ignore this email.</p>
        """
    })

def send_password_reset_email(email: str, otp: str):
    resend.Emails.send({
        "from": "onboarding@resend.dev",
        "to": email,
        "subject": "Password Reset OTP",
        "html": f"""
        <h2>Password Reset</h2>
        <p>Your OTP for password reset is:</p>
        <h1 style="color: #E53E3E; letter-spacing: 8px;">{otp}</h1>
        <p>This OTP will expire in 10 minutes.</p>
        <p>If you didn't request this, please secure your account immediately.</p>
        """
    })