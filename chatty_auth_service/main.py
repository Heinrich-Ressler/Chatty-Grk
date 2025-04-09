from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import User
from schemas import UserCreate, UserLogin
from passlib.context import CryptContext
import smtplib
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(title="Chatty Auth Service")
Instrumentator().instrument(app).expose(app)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@app.post("/register")
async def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = pwd_context.hash(user.password)
    new_user = User(username=user.username, email=user.email, hashed_password=hashed_password, is_active=False)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login("chatty@example.com", "password")
            message = f"Subject: Подтверждение\n\nПодтвердите: http://localhost/auth/verify/{new_user.id}"
            server.sendmail("chatty@example.com", user.email, message)
    except Exception:
        raise HTTPException(status_code=500, detail="Email error")
    return {"message": f"User {user.username} registered, check your email"}


@app.post("/login")
async def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not pwd_context.verify(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    if not db_user.is_active:
        raise HTTPException(status_code=400, detail="Account not verified")
    return {"message": "Login successful", "token": "fake-jwt-token", "user_id": db_user.id}


@app.get("/verify/{user_id}")
async def verify_account(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db_user.is_active = True
    db.commit()
    return {"message": "Account verified"}