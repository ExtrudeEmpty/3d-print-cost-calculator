from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database import get_db
from models import Printer, Material, Settings, Order, Maintenance, Dryer, FilamentType
from sqlalchemy import func

templates = Jinja2Templates(directory="templates")

router = APIRouter(tags=["pages"])


@router.get("/")
def index():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/dashboard")


@router.get("/dashboard")
def dashboard_page(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(request, "dashboard.html")


@router.get("/dryers")
def dryers_page(request: Request, db: Session = Depends(get_db)):
    filament_types = db.query(FilamentType).order_by(FilamentType.name).all()
    ft_list = [{"id": ft.id, "name": ft.name} for ft in filament_types]
    return templates.TemplateResponse(request, "dryers.html", {"filament_types": ft_list})


@router.get("/orders/new")
def new_order_page(request: Request, db: Session = Depends(get_db)):
    printers = db.query(Printer).filter(Printer.is_active == True).order_by(Printer.name).all()
    materials = db.query(Material).filter(Material.is_active == True).order_by(Material.name).all()
    dryers = db.query(Dryer).filter(Dryer.is_active == True).order_by(Dryer.name).all()
    
    # Convert to dictionaries for JSON serialization in template
    printers_list = [
        {
            "id": p.id, 
            "name": p.name, 
            "preferred_dryer_id": p.preferred_dryer_id,
            "has_heated_chamber": p.has_heated_chamber
        } for p in printers
    ]
    materials_list = []
    for m in materials:
        m_dict = {
            "id": m.id, 
            "name": m.name,
            "filament_type_id": m.filament_type_id,
        }
        if m.filament_type:
            m_dict.update({
                "filament_type_name": m.filament_type.name,
                "needs_dryer": m.filament_type.needs_dryer,
                "needs_chamber": m.filament_type.needs_chamber,
                "suggested_dryer_mode": m.filament_type.dryer_mode_default,
                "suggested_dryer_pre_hours": float(m.filament_type.dryer_hours)
            })
        else:
            m_dict.update({
                "filament_type_name": "Unknown",
                "needs_dryer": False,
                "needs_chamber": False,
                "suggested_dryer_mode": "none",
                "suggested_dryer_pre_hours": 0.0
            })
        materials_list.append(m_dict)

    dryers_list = [
        {
            "id": d.id, 
            "name": d.name, 
            "has_ams": d.has_ams
        } for d in dryers
    ]

    filament_types = db.query(FilamentType).order_by(FilamentType.name).all()
    ft_list = [{"id": ft.id, "name": ft.name, "default_density": float(ft.default_density)} for ft in filament_types]

    return templates.TemplateResponse(request, "order_new.html", {
        "printers": printers_list,
        "materials": materials_list,
        "dryers": dryers_list,
        "filament_types": ft_list
    })


@router.get("/orders")
def orders_page(request: Request):
    return templates.TemplateResponse(request, "order_list.html")


@router.get("/printers")
def printers_page(request: Request, db: Session = Depends(get_db)):
    filament_types = db.query(FilamentType).order_by(FilamentType.name).all()
    ft_list = [{"id": ft.id, "name": ft.name, "default_density": float(ft.default_density)} for ft in filament_types]
    dryers = db.query(Dryer).filter(Dryer.is_active == True).order_by(Dryer.name).all()
    dryers_list = [{"id": d.id, "name": d.name, "has_ams": d.has_ams} for d in dryers]
    return templates.TemplateResponse(request, "printer_list.html", {
        "filament_types": ft_list,
        "dryers": dryers_list
    })


@router.get("/materials")
def materials_page(request: Request, db: Session = Depends(get_db)):
    filament_types = db.query(FilamentType).order_by(FilamentType.name).all()
    ft_list = [{"id": ft.id, "name": ft.name, "default_density": float(ft.default_density)} for ft in filament_types]
    return templates.TemplateResponse(request, "material_list.html", {
        "filament_types": ft_list
    })


@router.get("/maintenance")
def maintenance_page(request: Request, db: Session = Depends(get_db)):
    printers = db.query(Printer).filter(Printer.is_active == True).order_by(Printer.name).all()
    # Convert to plain dicts for {{ printers | tojson }} in template
    printers_json = [{"id": p.id, "name": p.name} for p in printers]
    return templates.TemplateResponse(request, "maintenance_list.html", {
        "printers": printers_json,
    })


@router.get("/settings")
def settings_page(request: Request, db: Session = Depends(get_db)):
    settings = db.query(Settings).filter(Settings.id == 1).first()
    if not settings:
        settings = Settings(id=1)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return templates.TemplateResponse(request, "settings.html", {
        "settings": settings,
    })
