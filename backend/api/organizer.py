from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import json

from backend.core.database import get_db
from backend.models.post import Post
from backend.models.ticket_type import TicketType
from backend.models.ticket import Ticket
from backend.models.user import User
from backend.schemas.post import PostOut
from backend.schemas.ticket_type import TicketTypeOut
from backend.schemas.ticket import TicketWithUserOut

router = APIRouter()

# 获取我发起的活动（posts 表中）
@router.get("/my_events/{user_id}")
def get_my_events(user_id: UUID, db: Session = Depends(get_db)):
    events = db.query(Post).filter(
        Post.user_id == user_id
    ).order_by(Post.created_at.desc()).all()

    result = []
    for event in events:
        if isinstance(event.image_urls, str):
            try:
                image_urls = json.loads(event.image_urls)
            except json.JSONDecodeError:
                image_urls = []
        else:
            image_urls = event.image_urls or []

        result.append({
            "id": str(event.id),
            "title": event.title,
            "content": event.content,
            "post_type": event.post_type,
            "created_at": event.created_at.isoformat(),
            "image_urls": image_urls,
            "likes": event.likes,
            "comments_count": event.comments_count,
            "user_id": str(event.user_id),
            "clicks": event.clicks,
            "location": event.location,
            "max_participants": event.max_participants,
            "start_date": event.start_date.isoformat() if event.start_date else None,
            "end_date": event.end_date.isoformat() if event.end_date else None,
            "price": event.price,
            "status": event.status,
            "city": event.city,
            "country": event.country,
            "is_active": event.is_active
        })

    # ✅ 返回纯 List（前端当前写法能直接解析）
    return JSONResponse(content=jsonable_encoder(result), media_type="application/json; charset=utf-8")

# 获取某活动的所有购票用户信息（tickets + users）
@router.get("/posts/{post_id}/tickets", response_model=List[TicketWithUserOut])
def get_all_tickets_for_post(post_id: UUID, db: Session = Depends(get_db)):
    tickets = db.query(Ticket, User).join(User, Ticket.user_id == User.id).filter(
        Ticket.event_id == post_id
    ).all()

    result = []
    for ticket, user in tickets:
        result.append({
            "ticket_id": ticket.id,
            "user_id": user.id,
            "user_name": user.full_name,
            "ticket_type": ticket.ticket_type,
            "status": ticket.status,
            "valid_from": ticket.valid_from,
            "valid_until": ticket.valid_until
        })
    return result
