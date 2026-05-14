from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Dryer, DryerMaterialCalibration, Material, FilamentType
from schemas import DryerCreate, DryerUpdate, DryerResponse, CalibrationCreate, CalibrationResponse

router = APIRouter(prefix="/api/dryers", tags=["dryers"])

@router.get("", response_model=list[DryerResponse])
def list_dryers(active_only: bool = True, db: Session = Depends(get_db)):
    query = db.query(Dryer)
    if active_only:
        query = query.filter(Dryer.is_active == True)
    return query.order_by(Dryer.name).all()


@router.post("", response_model=DryerResponse, status_code=201)
def create_dryer(data: DryerCreate, db: Session = Depends(get_db)):
    dryer = Dryer(**data.model_dump())
    db.add(dryer)
    db.commit()
    db.refresh(dryer)
    return dryer


@router.get("/{dryer_id}", response_model=DryerResponse)
def get_dryer(dryer_id: int, db: Session = Depends(get_db)):
    dryer = db.query(Dryer).filter(Dryer.id == dryer_id).first()
    if not dryer:
        raise HTTPException(status_code=404, detail="Trockner nicht gefunden")
    return dryer


@router.put("/{dryer_id}", response_model=DryerResponse)
def update_dryer(dryer_id: int, data: DryerUpdate, db: Session = Depends(get_db)):
    dryer = db.query(Dryer).filter(Dryer.id == dryer_id).first()
    if not dryer:
        raise HTTPException(status_code=404, detail="Trockner nicht gefunden")
    
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(dryer, key, value)
        
    db.commit()
    db.refresh(dryer)
    return dryer


@router.delete("/{dryer_id}", status_code=204)
def delete_dryer(dryer_id: int, db: Session = Depends(get_db)):
    dryer = db.query(Dryer).filter(Dryer.id == dryer_id).first()
    if not dryer:
        raise HTTPException(status_code=404, detail="Trockner nicht gefunden")
    dryer.is_active = False
    db.commit()
    return None


@router.get("/{dryer_id}/calibrations", response_model=list[CalibrationResponse])
def get_dryer_calibrations(dryer_id: int, db: Session = Depends(get_db)):
    calibrations = db.query(DryerMaterialCalibration).filter(DryerMaterialCalibration.dryer_id == dryer_id).all()
    results = []
    for c in calibrations:
        results.append(CalibrationResponse(
            filament_type_id=c.filament_type_id,
            filament_type_name=c.filament_type.name,
            power_factor=float(c.power_factor),
            measured_at=c.measured_at,
        ))
    return results


@router.post("/{dryer_id}/calibrations", response_model=CalibrationResponse)
def save_dryer_calibration(dryer_id: int, data: CalibrationCreate, db: Session = Depends(get_db)):
    ft = db.query(FilamentType).filter(FilamentType.id == data.filament_type_id).first()
    if not ft:
        raise HTTPException(status_code=404, detail="Filament-Typ nicht gefunden")
    
    calib = db.query(DryerMaterialCalibration).filter(
        DryerMaterialCalibration.dryer_id == dryer_id,
        DryerMaterialCalibration.filament_type_id == data.filament_type_id
    ).first()

    if calib:
        calib.power_factor = data.power_factor
    else:
        calib = DryerMaterialCalibration(
            dryer_id=dryer_id,
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


@router.delete("/{dryer_id}/calibrations/{filament_type_id}", status_code=204)
def delete_dryer_calibration(dryer_id: int, filament_type_id: int, db: Session = Depends(get_db)):
    calib = db.query(DryerMaterialCalibration).filter(
        DryerMaterialCalibration.dryer_id == dryer_id,
        DryerMaterialCalibration.filament_type_id == filament_type_id
    ).first()
    
    if not calib:
        raise HTTPException(status_code=404, detail="Kalibrierung nicht gefunden")
        
    db.delete(calib)
    db.commit()
    return None
