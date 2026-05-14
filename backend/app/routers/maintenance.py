from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Maintenance, Printer
from schemas import MaintenanceCreate, MaintenanceResponse

router = APIRouter(prefix="/api/maintenance", tags=["maintenance"])


@router.get("", response_model=list[MaintenanceResponse])
def list_maintenance(printer_id: int = None, db: Session = Depends(get_db)):
    query = db.query(Maintenance)
    if printer_id:
        query = query.filter(Maintenance.printer_id == printer_id)
    records = query.order_by(Maintenance.date.desc()).all()
    
    # Get settings for labor rate calculation
    from models import Settings
    settings = db.query(Settings).first()
    
    response = []
    for r in records:
        labor_factor = 1.0
        if r.hourly_rate_type == "friends": labor_factor = float(settings.labor_factor_friends)
        elif r.hourly_rate_type == "private": labor_factor = float(settings.labor_factor_private)
        
        labor_cost = float(r.labor_hours) * float(settings.hourly_labor_rate) * labor_factor
        total_cost = float(r.cost) + labor_cost
        
        response.append(MaintenanceResponse(
            id=r.id,
            printer_id=r.printer_id,
            printer_name=r.printer.name,
            date=r.date,
            part_type=r.part_type,
            cost=float(r.cost),
            labor_hours=float(r.labor_hours),
            hourly_rate_type=r.hourly_rate_type,
            total_cost=total_cost,
            notes=r.notes,
        ))
    return response


@router.post("", response_model=MaintenanceResponse, status_code=201)
def create_maintenance(data: MaintenanceCreate, db: Session = Depends(get_db)):
    printer = db.query(Printer).filter(Printer.id == data.printer_id).first()
    if not printer:
        raise HTTPException(status_code=404, detail="Drucker nicht gefunden")

    record = Maintenance(**data.model_dump(exclude_unset=True))
    db.add(record)
    db.commit()
    db.refresh(record)

    from models import Settings
    settings = db.query(Settings).first()
    labor_factor = 1.0
    if record.hourly_rate_type == "friends": labor_factor = float(settings.labor_factor_friends)
    elif record.hourly_rate_type == "private": labor_factor = float(settings.labor_factor_private)
    
    labor_cost = float(record.labor_hours) * float(settings.hourly_labor_rate) * labor_factor
    total_cost = float(record.cost) + labor_cost

    return MaintenanceResponse(
        id=record.id,
        printer_id=record.printer_id,
        printer_name=printer.name,
        date=record.date,
        part_type=record.part_type,
        cost=float(record.cost),
        labor_hours=float(record.labor_hours),
        hourly_rate_type=record.hourly_rate_type,
        total_cost=total_cost,
        notes=record.notes,
    )


@router.delete("/{record_id}", status_code=204)
def delete_maintenance(record_id: int, db: Session = Depends(get_db)):
    record = db.query(Maintenance).filter(Maintenance.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Wartungseintrag nicht gefunden")
    db.delete(record)
    db.commit()
    return None
