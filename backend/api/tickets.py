from fastapi import APIRouter, Depends, HTTPException, Request, Body, Query, status
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime
from fastapi.encoders import jsonable_encoder
from backend.core.database import get_db
from backend.models.ticket import Ticket
from backend.models.ticket_type import TicketType
from backend.models.post import Post
from backend.models.user import User
from backend.schemas.ticket import TicketOut, FreeTicketRegisterRequest, FreeTicketCancelRequest
from backend.schemas.ticket_type import TicketTypeCreate, TicketTypeOut, TicketTypeToggle
from qrcode import make as make_qrcode
from io import BytesIO
import base64
from backend.core.dependencies import get_current_user
from fastapi.responses import JSONResponse

router = APIRouter(tags=["Tickets"])

@router.get("/posts/{post_id}/ticket_types", response_model=list[TicketTypeOut])
def get_ticket_types_by_post(
    post_id: UUID,
    include_all: bool = False,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    user_id = user["user_id"]

    # 查询票种列表
    query = db.query(TicketType).filter(TicketType.post_id == str(post_id))
    if not include_all:
        query = query.filter(TicketType.is_active == True)

    ticket_types = query.order_by(TicketType.created_at.asc()).all()

    result = []
    for ticket_type in ticket_types:
        # 查询当前用户是否已领此票种（免费票）
        has_registered = db.query(Ticket).filter_by(
            user_id=user_id,
            event_id=post_id,
            ticket_type=ticket_type.name,
            price=0  # 确保是免费票
        ).first() is not None

        # 转为 dict 并添加字段
        ticket_dict = TicketTypeOut.model_validate(ticket_type).model_dump()
        ticket_dict["has_registered"] = has_registered

        result.append(TicketTypeOut(**ticket_dict))

    return result


@router.post("/posts/{post_id}/create_ticket_type")
def create_ticket_type_for_post(post_id: UUID, ticket_data: TicketTypeCreate, db: Session = Depends(get_db)):
    existing = db.query(TicketType).filter(
        TicketType.post_id == post_id,
        TicketType.name == ticket_data.name
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="票种名称已存在，请更换名称")

    new_ticket_type = TicketType(
        post_id=post_id,
        name=ticket_data.name,
        price=ticket_data.price,
        quantity=ticket_data.quantity,
        valid_from=ticket_data.valid_from,
        valid_until=ticket_data.valid_until,
        sale_start=ticket_data.sale_start,
        sale_end=ticket_data.sale_end,
        ticket_category=ticket_data.ticket_category,
        user_role=ticket_data.user_role,
        is_active=False
    )
    db.add(new_ticket_type)
    db.commit()
    db.refresh(new_ticket_type)
    
    return JSONResponse(
        content=jsonable_encoder(new_ticket_type),
        media_type="application/json; charset=utf-8"
    )

@router.get("/user_tickets/{user_id}", response_model=list[TicketOut])
def get_user_tickets(user_id: UUID, status: str, db: Session = Depends(get_db)):
    if status not in ["valid", "expired"]:
        raise HTTPException(status_code=400, detail="状态无效")
    return db.query(Ticket).filter(Ticket.user_id == user_id, Ticket.status == status).all()


@router.get("/tickets/{ticket_id}", response_model=TicketOut)
def get_ticket_details(ticket_id: UUID, db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="未找到该票")
    return ticket


@router.post("/tickets/buy_ticket")
def buy_ticket(user_id: UUID, ticket_type_id: UUID, db: Session = Depends(get_db)):
    now = datetime.utcnow()
    ticket_type = db.query(TicketType).filter(TicketType.id == ticket_type_id).first()
    if not ticket_type:
        raise HTTPException(status_code=404, detail="票种不存在")

    if ticket_type.quantity <= 0:
        raise HTTPException(status_code=400, detail="票已售罄")
    if not (ticket_type.sale_start <= now <= ticket_type.sale_end):
        raise HTTPException(status_code=400, detail="不在售票时间范围")

    existing = db.query(Ticket).filter(
        Ticket.user_id == user_id,
        Ticket.ticket_type == ticket_type.name,
        Ticket.event_id == ticket_type.post_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="你已购买该票种")

    ticket_type.quantity -= 1

    new_ticket = Ticket(
        user_id=user_id,
        event_id=ticket_type.post_id,
        ticket_type=ticket_type.name,
        valid_from=ticket_type.valid_from,
        valid_until=ticket_type.valid_until,
        status="valid"
    )
    db.add(new_ticket)
    db.flush()

    qr_img = make_qrcode(str(new_ticket.id))
    buf = BytesIO()
    qr_img.save(buf, format="PNG")
    new_ticket.qr_code = base64.b64encode(buf.getvalue()).decode("utf-8")

    db.commit()
    return {"message": "购票成功", "ticket_id": str(new_ticket.id)}

@router.post("/tickets/register_free_ticket")
def register_free_ticket(
    request: FreeTicketRegisterRequest,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    user_id = user["user_id"]
    # 1. 查询票种是否存在、激活、价格为 0
    ticket_type = db.query(TicketType).filter(
        TicketType.id == request.ticket_type_id,
        TicketType.is_active == True,
        TicketType.price == 0
    ).first()
    if not ticket_type:
        raise HTTPException(status_code=400, detail="该票种不存在、未激活或不是免费票")

    # 2. 检查该 post 是否存在且激活
    post = db.query(Post).filter(
        Post.id == request.post_id,
        Post.is_active == True
    ).first()
    if not post:
        raise HTTPException(status_code=400, detail="活动不存在或未激活")

    # 3. 检查是否已报名（通过 tickets 表判断）
    existing = db.query(Ticket).filter_by(
        user_id=user_id,
        event_id=post.id,
        ticket_type=ticket_type.name,
        price=0  # 限定为免费票
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="你已报名该活动")

    # 4. 创建票（ticket）
    new_ticket = Ticket(
        user_id=user_id,
        event_id=post.id,
        ticket_type=ticket_type.name,
        price=0,
        status="valid",
        valid_from=post.start_time,
        valid_until=post.end_time,
        qr_code="free_ticket"  # 后续可生成真实 JWT
    )
    db.add(new_ticket)
    db.flush()  # 获取 new_ticket.id

    # 5. 更新剩余票数
    if ticket_type.remaining_quantity is not None and ticket_type.remaining_quantity > 0:
        ticket_type.remaining_quantity -= 1
        db.add(ticket_type)
    else:
        raise HTTPException(status_code=400, detail="该票种已满员")

    db.commit()
    return {"message": "报名成功"}

@router.delete("/ticket_types/{ticket_type_id}")
def delete_ticket_type(ticket_type_id: UUID, db: Session = Depends(get_db)):
    ticket_type = db.query(TicketType).filter(TicketType.id == ticket_type_id).first()
    if not ticket_type:
        raise HTTPException(status_code=404, detail="票种不存在")

    sold_count = db.query(Ticket).filter(
        Ticket.ticket_type == ticket_type.name,
        Ticket.event_id == ticket_type.post_id
    ).count()
    if sold_count > 0:
        raise HTTPException(status_code=400, detail="该票种已售出，无法删除")

    db.delete(ticket_type)
    db.commit()
    return {"message": "删除票种成功"}

@router.post("/ticket_types/{ticket_type_id}/toggle_activation", response_model=TicketTypeOut)
def toggle_ticket_type_activation(
    ticket_type_id: UUID,
    toggle: TicketTypeToggle,
    db: Session = Depends(get_db)
):
    ticket_type = db.query(TicketType).filter(TicketType.id == ticket_type_id).first()
    if not ticket_type:
        raise HTTPException(status_code=404, detail="票种不存在")

    sold = db.query(Ticket).filter(
        Ticket.ticket_type == ticket_type.name,
        Ticket.event_id == ticket_type.post_id
    ).count()
    if sold > 0 and not toggle.activate:
        raise HTTPException(status_code=400, detail="该票种已售出，不能反激活")

    ticket_type.is_active = toggle.activate
    db.commit()
    db.refresh(ticket_type)
    return ticket_type

@router.post("/tickets/cancel_free_ticket")
def cancel_free_ticket(
    request: FreeTicketCancelRequest,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    user_id = user["user_id"]
    # 1. 查询活动是否存在
    post = db.query(Post).filter(
        Post.id == request.post_id,
        Post.is_active == True
    ).first()
    if not post:
        raise HTTPException(status_code=404, detail="活动不存在或未激活")

    # 2. 查询报名记录
    registration = db.query(EventRegistration).filter_by(
        user_id=user_id,
        event_id=post.id,
        registration_type="ticketed",
        status="confirmed"
    ).first()
    if not registration:
        raise HTTPException(status_code=400, detail="你尚未报名该活动")

    # 3. 查询对应 ticket
    ticket = db.query(Ticket).filter(
        Ticket.id == registration.ticket_id,
        Ticket.user_id == user_id
    ).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="对应票券未找到")

    # 4. 查询对应 ticket_type
    ticket_type = db.query(TicketType).filter(
        TicketType.name == ticket.ticket_type,
        TicketType.post_id == post.id,
        TicketType.price == 0
    ).first()

    # 5. 删除报名和票，并恢复余量
    db.delete(registration)
    db.delete(ticket)

    if ticket_type and ticket_type.remaining_quantity is not None:
        ticket_type.remaining_quantity += 1
        db.add(ticket_type)

    db.commit()
    return {"message": "已成功取消报名"}
