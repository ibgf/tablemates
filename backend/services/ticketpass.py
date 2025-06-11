# ✅ 文件：services/ticketpass.py

import jwt
from datetime import datetime, timedelta
from backend.core.config import settings
from jwt import ExpiredSignatureError, InvalidTokenError


def decode_ticketpass_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload
    except ExpiredSignatureError:
        raise ValueError("二维码已过期")
    except InvalidTokenError:
        raise ValueError("二维码无效")


def create_ticketpass_token(user_id: str, role: str, assoc: str = "", claims: list[str] = None) -> str:
    now = datetime.utcnow()
    payload = {
        "user_id": user_id,
        "role": role,
        "assoc": assoc,
        "claims": claims or [],
        "iat": now,
        "exp": now + timedelta(hours=24),
    }

    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    return token
