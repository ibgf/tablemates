#  ✅ 文件路径：api/ticket_discounts.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime

from backend.core.database import get_db
from backend.models.ticket_discount import TicketDiscount
from backend.schemas.ticket_discount import TicketDiscountCreate, TicketDiscountOut

router = APIRouter(tags=["Ticket Discounts"])

@router.post("/discounts", response_model=TicketDiscountOut)
def create_discount(data: TicketDiscountCreate, db: Session = Depends(get_db)):
    new_discount = TicketDiscount(**data.model_dump())
    db.add(new_discount)
    db.commit()
    db.refresh(new_discount)
    return new_discount

@router.get("/discounts", response_model=list[TicketDiscountOut])
def list_discounts(db: Session = Depends(get_db)):
    return db.query(TicketDiscount).order_by(TicketDiscount.created_at.desc()).all()

@router.post("/discounts/validate", response_model=TicketDiscountOut)
def validate_discount(code: str, ticket_type_id: UUID, db: Session = Depends(get_db)):
    now = datetime.utcnow()
    discount = db.query(TicketDiscount).filter(
        TicketDiscount.code == code,
        TicketDiscount.ticket_type_id == ticket_type_id,
        TicketDiscount.valid_from <= now,
        TicketDiscount.valid_until >= now,
        TicketDiscount.is_active == True,
    ).first()
    if not discount:
        raise HTTPException(status_code=404, detail="优惠码无效或已过期")
    if discount.usage_limit and discount.used_count >= discount.usage_limit:
        raise HTTPException(status_code=400, detail="优惠码已达最大使用次数")
    return discount

@router.delete("/discounts/{discount_id}")
def delete_discount(discount_id: UUID, db: Session = Depends(get_db)):
    discount = db.query(TicketDiscount).filter(TicketDiscount.id == discount_id).first()
    if not discount:
        raise HTTPException(status_code=404, detail="找不到该优惠信息")
    db.delete(discount)
    db.commit()
    return {"message": "已删除"}
