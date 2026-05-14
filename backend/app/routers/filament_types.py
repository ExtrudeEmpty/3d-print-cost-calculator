from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import FilamentType
from schemas import FilamentTypeCreate, FilamentTypeUpdate, FilamentTypeResponse
from calculator import parse_time_string

router = APIRouter(prefix="/api/filament-types", tags=["filament-types"])

@router.get("/", response_model=List[FilamentTypeResponse])
def get_filament_types(db: Session = Depends(get_db)):
    return db.query(FilamentType).order_by(FilamentType.name).all()

@router.post("/", response_model=FilamentTypeResponse)
def create_filament_type(ft: FilamentTypeCreate, db: Session = Depends(get_db)):
    try:
        ft.dryer_hours = parse_time_string(ft.dryer_hours, "hours")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    db_ft = FilamentType(**ft.model_dump())
    db.add(db_ft)
    db.commit()
    db.refresh(db_ft)
    return db_ft

@router.get("/{ft_id}", response_model=FilamentTypeResponse)
def get_filament_type(ft_id: int, db: Session = Depends(get_db)):
    ft = db.query(FilamentType).filter(FilamentType.id == ft_id).first()
    if not ft:
        raise HTTPException(status_code=404, detail="Filament type not found")
    return ft

@router.put("/{ft_id}", response_model=FilamentTypeResponse)
def update_filament_type(ft_id: int, ft_update: FilamentTypeUpdate, db: Session = Depends(get_db)):
    db_ft = db.query(FilamentType).filter(FilamentType.id == ft_id).first()
    if not db_ft:
        raise HTTPException(status_code=404, detail="Filament type not found")
    
    update_data = ft_update.model_dump(exclude_unset=True)
    if "dryer_hours" in update_data:
        try:
            update_data["dryer_hours"] = parse_time_string(update_data["dryer_hours"], "hours")
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    for key, value in update_data.items():
        setattr(db_ft, key, value)
    
    db.commit()
    db.refresh(db_ft)
    return db_ft

@router.delete("/{ft_id}")
def delete_filament_type(ft_id: int, db: Session = Depends(get_db)):
    db_ft = db.query(FilamentType).filter(FilamentType.id == ft_id).first()
    if not db_ft:
        raise HTTPException(status_code=404, detail="Filament type not found")
    
    db.delete(db_ft)
    db.commit()
    return {"message": "Filament type deleted"}
