#  ✅ 文件路径：api/ticket_scan.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime

from backend.core.database import get_db
from backend.models.ticket_scan_log import TicketScanLog
from backend.models.ticket import Ticket
from backend.schemas.ticket_scan_log import TicketScanLogCreate, TicketScanLogOut

router = APIRouter(tags=["Ticket Scan Logs"])

@router.post("/tickets/{ticket_id}/scan", response_model=TicketScanLogOut)
def scan_ticket(ticket_id: UUID, data: TicketScanLogCreate, db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="票不存在")

    scan_log = TicketScanLog(
        ticket_id=ticket_id,
        scan_type=data.scan_type,
        entry_date=data.entry_date,
        device_id=data.device_id
    )
    db.add(scan_log)
    db.commit()
    db.refresh(scan_log)
    return scan_log

@router.get("/tickets/{ticket_id}/scans", response_model=list[TicketScanLogOut])
def get_ticket_scans(ticket_id: UUID, db: Session = Depends(get_db)):
    return db.query(TicketScanLog).filter(TicketScanLog.ticket_id == ticket_id).order_by(TicketScanLog.scan_time.desc()).all()
