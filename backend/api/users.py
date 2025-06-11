from fastapi import APIRouter, Depends, HTTPException, Request, Body
from sqlalchemy.orm import Session
from uuid import UUID
from backend.core.database import get_db
from backend.models.user import User, UserAuth
from backend.schemas.user import UserCreate, UserLogin, UserOut, AuthBinding
import bcrypt
import jwt
import os
import datetime
from pydantic import BaseModel, EmailStr
from backend.utils.email_utils import generate_verification_code, send_verification_email
from datetime import timedelta
from backend.core.security import create_access_token, create_refresh_token, verify_password
from backend.schemas.auth import LoginRequest  # 假设你已经定义
from backend.core.config import settings


router = APIRouter(tags=["Users"])

# **第 1 步：发送验证码**
class SendCodeRequest(BaseModel):
    email_or_phone: str

@router.post("/send-code")
def send_code(request: SendCodeRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(
        (User.email == request.email_or_phone) | (User.phone == request.email_or_phone)
    ).first()

    verification_code = generate_verification_code()
    expires_at = datetime.datetime.utcnow() + datetime.timedelta(minutes=10)

    if user:
        # 旧用户，重新发送验证码
        user.verification_code = verification_code
        user.verification_expires_at = expires_at
    else:
        # 新用户，创建临时记录（不存密码）
        new_user = User(
            email=request.email_or_phone if "@" in request.email_or_phone else None,
            phone=request.email_or_phone if "@" not in request.email_or_phone else None,
            is_active=False,
            verification_code=verification_code,
            verification_expires_at=expires_at
        )
        db.add(new_user)
    
    db.commit()
    
    # 发送验证码
    if "@" in request.email_or_phone:
        send_verification_email(request.email_or_phone, verification_code)

    return {"message": "验证码已发送，请检查你的邮箱或短信"}

# **第 2 步：验证验证码**
class VerifyCodeRequest(BaseModel):
    email_or_phone: str
    code: str

@router.post("/verify-code")
def verify_code(request: VerifyCodeRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(
        (User.email == request.email_or_phone) | (User.phone == request.email_or_phone)
    ).first()

    if not user:
        raise HTTPException(status_code=400, detail="用户不存在")

    if not user.verification_code or user.verification_expires_at < datetime.datetime.utcnow():
        raise HTTPException(status_code=400, detail="验证码已过期，请重新发送")

    if user.verification_code != request.code:
        raise HTTPException(status_code=400, detail="验证码错误")

    # 验证通过，清除验证码
    user.verification_code = None
    user.verification_expires_at = None
    db.commit()

    return {"message": "验证码正确，请设置密码"}

# **第 3 步：设置密码，完成注册**
class RegisterRequest(BaseModel):
    email_or_phone: str
    password: str

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

@router.post("/register")
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(
        (User.email == request.email_or_phone) | (User.phone == request.email_or_phone)
    ).first()

    if not user:
        raise HTTPException(status_code=400, detail="用户未验证，请先获取验证码")

    if len(request.password) < 8:
        raise HTTPException(status_code=400, detail="密码至少8位")

    # 存储密码并激活用户
    user.password = hash_password(request.password)
    user.is_active = True
    db.commit()
    db.refresh(user)  # ✅ 确保数据库同步更新

    return {"message": "注册成功", "user_id": user.id, "email": user.email, "phone": user.phone}

# **重发验证码**
@router.post("/resend-code")
def resend_code(request: SendCodeRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(
        (User.email == request.email_or_phone) | (User.phone == request.email_or_phone)
    ).first()

    if not user:
        raise HTTPException(status_code=400, detail="用户不存在")

    if user.is_active:
        raise HTTPException(status_code=400, detail="账户已激活，无需验证码")

    verification_code = generate_verification_code()
    expires_at = datetime.datetime.utcnow() + datetime.timedelta(minutes=10)

    user.verification_code = verification_code
    user.verification_expires_at = expires_at
    db.commit()

    send_verification_email(request.email_or_phone, verification_code)

    return {"message": "验证码已重新发送，请检查邮箱或短信"}

# **登录**
class LoginRequest(BaseModel):
    email_or_phone: str
    password: str

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

#  def create_access_token(user_id: int):
#     expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=12)  # 12小时有效期
#     payload = {"sub": str(user_id), "exp": expiration}
#     return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(
        (User.email == request.email_or_phone) | (User.phone == request.email_or_phone)
    ).first()

    if not user or not verify_password(request.password, user.password):
        raise HTTPException(status_code=401, detail="手机号/邮箱或密码错误")

    # access_token = create_access_token(user.id)
    # return {"message": "登录成功", "token": access_token, "user_id": str(user.id)}

    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token = create_refresh_token(
        data={"sub": str(user.id)}, expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )

    return {
        "message": "登录成功",
        "token": access_token,
        "refresh_token": refresh_token,
        "user_id": str(user.id)
    }


@router.post("/refresh")
def refresh_token(
    refresh_token: str = Body(...),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")

        user_uuid = UUID(user_id)
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except (JWTError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token")

    # ✅ 增加用户是否存在的判断
    user = db.query(User).filter(User.id == user_uuid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 生成新 access_token
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=15)
    )
    return {"access_token": access_token}
