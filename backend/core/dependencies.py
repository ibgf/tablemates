from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from uuid import UUID
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError, ExpiredSignatureError
from sqlalchemy.orm import Session
from backend.core.config import settings
from backend.core.database import get_db
from backend.models.user import User

security = HTTPBearer()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="无效的身份凭证")
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="登录信息已过期，请重新登录")
    except JWTError:
        raise HTTPException(status_code=401, detail="无效的访问令牌")
    
    try:
        user_uuid = UUID(user_id)  # ✅ 正确转换为 UUID 类型
    except ValueError:
        raise HTTPException(status_code=400, detail="非法用户 ID")

    user = db.query(User).filter(User.id == user_uuid).first()
    if user is None:

        raise HTTPException(status_code=401, detail="用户不存在")

    # ✅ 返回 dict，而不是 User 实例
    return {
        "user_id": str(user.id),
        "email": user.email,
        "phone": user.phone,
        "full_name": user.full_name,
        # 你还可以添加更多字段
    }
