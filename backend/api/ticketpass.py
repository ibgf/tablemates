from fastapi import APIRouter, HTTPException, Depends
from backend.services.ticketpass import create_ticketpass_token, decode_ticketpass_token

router = APIRouter(tags=["TicketPass"])

@router.get("/ticketpass/{user_id}")
def generate_ticketpass(user_id: str):
    # 可改为查数据库判断 role 等
    token = create_ticketpass_token(user_id, role="verified", assoc="IBGF", claims=["vip"])
    return {"token": token}

@router.post("/ticketpass/verify")
def verify_ticketpass_token(token: str):
    try:
        payload = decode_ticketpass_token(token)
        return {"valid": True, "data": payload}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
