from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Printer, PrinterMaterialCalibration, Material, FilamentType
from schemas import PrinterCreate, PrinterUpdate, PrinterResponse, CalibrationCreate, CalibrationResponse
from calculator import parse_time_string

router = APIRouter(prefix="/api/printers", tags=["printers"])


@router.get("", response_model=list[PrinterResponse])
def list_printers(active_only: bool = True, db: Session = Depends(get_db)):
    query = db.query(Printer)
    if active_only:
        query = query.filter(Printer.is_active == True)
    return query.order_by(Printer.name).all()


@router.get("/{printer_id}", response_model=PrinterResponse)
def get_printer(printer_id: int, db: Session = Depends(get_db)):
    printer = db.query(Printer).filter(Printer.id == printer_id).first()
    if not printer:
        raise HTTPException(status_code=404, detail="Drucker nicht gefunden")
    return printer


@router.post("", response_model=PrinterResponse, status_code=201)
def create_printer(data: PrinterCreate, db: Session = Depends(get_db)):
    try:
        data.expected_lifetime_hours = int(parse_time_string(data.expected_lifetime_hours, "hours"))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    printer = Printer(**data.model_dump())
    db.add(printer)
    db.commit()
    db.refresh(printer)
    return printer


@router.put("/{printer_id}", response_model=PrinterResponse)
def update_printer(printer_id: int, data: PrinterUpdate, db: Session = Depends(get_db)):
    printer = db.query(Printer).filter(Printer.id == printer_id).first()
    if not printer:
        raise HTTPException(status_code=404, detail="Drucker nicht gefunden")
    update_data = data.model_dump(exclude_unset=True)
    if "expected_lifetime_hours" in update_data:
        try:
            update_data["expected_lifetime_hours"] = int(parse_time_string(update_data["expected_lifetime_hours"], "hours"))
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    for key, value in update_data.items():
        setattr(printer, key, value)
    db.commit()
    db.refresh(printer)
    return printer


@router.delete("/{printer_id}", status_code=204)
def delete_printer(printer_id: int, db: Session = Depends(get_db)):
    printer = db.query(Printer).filter(Printer.id == printer_id).first()
    if not printer:
        raise HTTPException(status_code=404, detail="Drucker nicht gefunden")
    printer.is_active = False
    db.commit()
    return None


@router.get("/{printer_id}/calibrations", response_model=list[CalibrationResponse])
def get_printer_calibrations(printer_id: int, db: Session = Depends(get_db)):
    calibrations = db.query(PrinterMaterialCalibration).filter(PrinterMaterialCalibration.printer_id == printer_id).all()
    results = []
    for c in calibrations:
        results.append(CalibrationResponse(
            filament_type_id=c.filament_type_id,
            filament_type_name=c.filament_type.name,
            power_factor=float(c.power_factor),
            measured_at=c.measured_at,
        ))
    return results


@router.post("/{printer_id}/calibrations", response_model=CalibrationResponse)
def save_printer_calibration(printer_id: int, data: CalibrationCreate, db: Session = Depends(get_db)):
    ft = db.query(FilamentType).filter(FilamentType.id == data.filament_type_id).first()
    if not ft:
        raise HTTPException(status_code=404, detail="Filament-Typ nicht gefunden")
    
    calib = db.query(PrinterMaterialCalibration).filter(
        PrinterMaterialCalibration.printer_id == printer_id,
        PrinterMaterialCalibration.filament_type_id == data.filament_type_id
    ).first()

    if calib:
        calib.power_factor = data.power_factor
    else:
        calib = PrinterMaterialCalibration(
            printer_id=printer_id,
            filament_type_id=data.filament_type_id,
            power_factor=data.power_factor
        )
        db.add(calib)

    db.commit()
    db.refresh(calib)
    
    return CalibrationResponse(
        filament_type_id=calib.filament_type_id,
        filament_type_name=ft.name,
        power_factor=float(calib.power_factor),
        measured_at=calib.measured_at,
    )


@router.delete("/{printer_id}/calibrations/{filament_type_id}", status_code=204)
def delete_printer_calibration(printer_id: int, filament_type_id: int, db: Session = Depends(get_db)):
    calib = db.query(PrinterMaterialCalibration).filter(
        PrinterMaterialCalibration.printer_id == printer_id,
        PrinterMaterialCalibration.filament_type_id == filament_type_id
    ).first()
    
    if not calib:
        raise HTTPException(status_code=404, detail="Kalibrierung nicht gefunden")
        
    db.delete(calib)
    db.commit()
    return None
