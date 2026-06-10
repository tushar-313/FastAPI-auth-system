from fastapi import FastAPI
from app.routers import auth

app = FastAPI(
    title="Auth API",
    description="JWT + Google OAuth + Email OTP",
    version="1.0.0"
)

app.include_router(auth.router)

@app.get("/")
def read_root():
    return {"message": "Auth API is running!"}

@app.get("/health")
def health_check():
    return {"status": "ok"}