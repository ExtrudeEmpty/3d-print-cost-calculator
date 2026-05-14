from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from database import engine, Base
from models import Settings
from database import SessionLocal

# Create all tables on startup
Base.metadata.create_all(bind=engine)

# Seed default settings if they don't exist
db = SessionLocal()
try:
    existing = db.query(Settings).filter(Settings.id == 1).first()
    if not existing:
        db.add(Settings(id=1))
        db.commit()
finally:
    db.close()

app = FastAPI(title="3D-Druck Kostenrechner", version="1.0.0")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Import and include all routers
from routers.printers import router as printers_router
from routers.dryers import router as dryers_router
from routers.materials import router as materials_router
from routers.orders import router as orders_router
from routers.maintenance import router as maintenance_router
from routers.settings import router as settings_router
from routers.dashboard import router as dashboard_router
from routers.pages import router as pages_router
from routers.filament_types import router as filament_types_router

app.include_router(printers_router)
app.include_router(dryers_router)
app.include_router(materials_router)
app.include_router(orders_router)
app.include_router(maintenance_router)
app.include_router(settings_router)
app.include_router(dashboard_router)
app.include_router(pages_router)
app.include_router(filament_types_router)


@app.get("/health")
def health():
    return {"status": "ok"}
