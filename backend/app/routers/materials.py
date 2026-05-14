from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Material
from schemas import MaterialCreate, MaterialUpdate, MaterialResponse

router = APIRouter(prefix="/api/materials", tags=["materials"])


@router.get("", response_model=list[MaterialResponse])
def list_materials(active_only: bool = True, db: Session = Depends(get_db)):
    query = db.query(Material)
    if active_only:
        query = query.filter(Material.is_active == True)
    materials = query.order_by(Material.name).all()
    
    # Populate filament_type_name
    for m in materials:
        if m.filament_type:
            m.filament_type_name = m.filament_type.name
    return materials


@router.get("/{material_id}", response_model=MaterialResponse)
def get_material(material_id: int, db: Session = Depends(get_db)):
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material nicht gefunden")
    
    if material.filament_type:
        material.filament_type_name = material.filament_type.name
    return material


@router.post("", response_model=MaterialResponse, status_code=201)
def create_material(data: MaterialCreate, db: Session = Depends(get_db)):
    material = Material(**data.model_dump())
    db.add(material)
    db.commit()
    db.refresh(material)
    return material


@router.put("/{material_id}", response_model=MaterialResponse)
def update_material(material_id: int, data: MaterialUpdate, db: Session = Depends(get_db)):
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material nicht gefunden")
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(material, key, value)
    db.commit()
    db.refresh(material)
    return material


@router.delete("/{material_id}", status_code=204)
def delete_material(material_id: int, db: Session = Depends(get_db)):
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material nicht gefunden")
    material.is_active = False
    db.commit()
    return None
