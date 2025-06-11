#  ✅ 文件路径：api/ticket_stats.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from backend.core.database import get_db
from backend.models.ticket_type_stats import TicketTypeStats
from backend.models.ticket import Ticket
from backend.models.ticket_refund import TicketRefund
from backend.schemas.ticket_type_stats import TicketTypeStatsOut

router = APIRouter(tags=["Ticket Type Stats"])

@router.get("/tickets/{ticket_type_id}/stats", response_model=TicketTypeStatsOut)
def get_ticket_type_stats(ticket_type_id: UUID, db: Session = Depends(get_db)):
    stats = db.query(TicketTypeStats).filter(TicketTypeStats.ticket_type_id == ticket_type_id).first()
    if not stats:
        raise HTTPException(status_code=404, detail="票种统计不存在")
    return stats

@router.post("/tickets/{ticket_type_id}/refresh_stats", response_model=TicketTypeStatsOut)
def refresh_ticket_type_stats(ticket_type_id: UUID, db: Session = Depends(get_db)):
    # 自动统计逻辑
    sold = db.query(Ticket).filter(Ticket.ticket_type == ticket_type_id.hex, Ticket.status == "valid").count()
    refunded = db.query(TicketRefund).join(Ticket).filter(
        Ticket.ticket_type == ticket_type_id.hex,
        TicketRefund.status == "approved"
    ).count()
    checked_in = 0  # 可接入 ticket_scan_logs.count() 逻辑

    stats = db.query(TicketTypeStats).filter(TicketTypeStats.ticket_type_id == ticket_type_id).first()
    if not stats:
        stats = TicketTypeStats(ticket_type_id=ticket_type_id)
        db.add(stats)

    stats.sold_quantity = sold
    stats.refund_quantity = refunded
    stats.checked_in_count = checked_in

    db.commit()
    db.refresh(stats)
    return stats
