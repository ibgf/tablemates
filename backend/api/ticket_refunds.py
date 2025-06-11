#  ✅ 文件路径：api/ticket_refunds.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime

from backend.core.database import get_db
from backend.models.ticket_refund import TicketRefund
from backend.models.ticket import Ticket
from backend.schemas.ticket_refund import TicketRefundCreate, TicketRefundOut, TicketRefundReview

router = APIRouter(tags=["Ticket Refunds"])

@router.post("/tickets/{ticket_id}/refund", response_model=TicketRefundOut)
def submit_refund(ticket_id: UUID, data: TicketRefundCreate, db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="未找到票据")

    refund = TicketRefund(
        ticket_id=ticket_id,
        user_id=data.user_id,
        refund_amount=data.refund_amount,
        reason=data.reason,
        status="pending"
    )
    db.add(refund)
    db.commit()
    db.refresh(refund)
    return refund

@router.get("/refunds/my", response_model=list[TicketRefundOut])
def get_my_refunds(user_id: UUID, db: Session = Depends(get_db)):
    return db.query(TicketRefund).filter(TicketRefund.user_id == user_id).order_by(TicketRefund.created_at.desc()).all()

@router.get("/refunds/pending", response_model=list[TicketRefundOut])
def list_pending_refunds(db: Session = Depends(get_db)):
    return db.query(TicketRefund).filter(TicketRefund.status == "pending").order_by(TicketRefund.created_at.asc()).all()

@router.post("/refunds/{refund_id}/review", response_model=TicketRefundOut)
def review_refund(refund_id: UUID, review: TicketRefundReview, db: Session = Depends(get_db)):
    refund = db.query(TicketRefund).filter(TicketRefund.id == refund_id).first()
    if not refund:
        raise HTTPException(status_code=404, detail="退款记录不存在")
    if refund.status != "pending":
        raise HTTPException(status_code=400, detail="该退票已处理")

    refund.status = review.status
    refund.reviewed_by = review.reviewed_by
    refund.reviewed_at = datetime.utcnow()

    db.commit()
    db.refresh(refund)
    return refund
