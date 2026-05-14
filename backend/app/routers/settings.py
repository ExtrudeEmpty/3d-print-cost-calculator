import os
import json
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import Settings
from schemas import SettingsResponse, SettingsUpdate, PreferenceResponse, LanguageUpdate, ThemeUpdate, FormattingUpdate

from sqlalchemy import text

router = APIRouter(prefix="/api/settings", tags=["settings"])


@router.get("/languages")
def get_available_languages():
    locales_dir = os.path.join("static", "locales")
    # If running from backend/app, adjust path
    if not os.path.exists(locales_dir):
        locales_dir = os.path.join(os.path.dirname(__file__), "..", "static", "locales")
    
    languages = []
    if os.path.exists(locales_dir):
        for filename in sorted(os.listdir(locales_dir)):
            if filename.endswith(".json"):
                code = filename[:-5]
                try:
                    with open(os.path.join(locales_dir, filename), "r", encoding="utf-8") as f:
                        data = json.load(f)
                        name = data.get("language_native", code.upper())
                        languages.append({"code": code, "name": name})
                except Exception:
                    languages.append({"code": code, "name": code.upper()})
    
    return languages


@router.get("", response_model=SettingsResponse)
def get_settings(db: Session = Depends(get_db)):
    settings = db.query(Settings).filter(Settings.id == 1).first()
    if not settings:
        # Auto-create with defaults if missing
        settings = Settings(id=1)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


@router.put("", response_model=SettingsResponse)
def update_settings(data: SettingsUpdate, db: Session = Depends(get_db)):
    settings = db.query(Settings).filter(Settings.id == 1).first()
    if not settings:
        settings = Settings(id=1)
        db.add(settings)
        db.commit()
        db.refresh(settings)

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(settings, key, value)
    db.commit()
    db.refresh(settings)
    return settings


@router.get("/preferences", response_model=PreferenceResponse)
def get_preferences(db: Session = Depends(get_db)):
    settings = db.query(Settings).filter(Settings.id == 1).first()
    if not settings:
        settings = Settings(id=1)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


@router.put("/language", response_model=PreferenceResponse)
def update_language(data: LanguageUpdate, db: Session = Depends(get_db)):
    settings = db.query(Settings).filter(Settings.id == 1).first()
    settings.language = data.language
    db.commit()
    db.refresh(settings)
    return settings


@router.get("/formatting", response_model=PreferenceResponse)
def get_formatting(db: Session = Depends(get_db)):
    settings = db.query(Settings).filter(Settings.id == 1).first()
    if not settings:
        settings = Settings(id=1)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


@router.put("/formatting", response_model=PreferenceResponse)
def update_formatting(data: FormattingUpdate, db: Session = Depends(get_db)):
    settings = db.query(Settings).filter(Settings.id == 1).first()
    if not settings:
        settings = Settings(id=1)
        db.add(settings)
        db.commit()
        db.refresh(settings)

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(settings, key, value)
    
    db.commit()
    db.refresh(settings)
    return settings


@router.put("/theme", response_model=PreferenceResponse)
def update_theme(data: ThemeUpdate, db: Session = Depends(get_db)):
    settings = db.query(Settings).filter(Settings.id == 1).first()
    settings.theme = data.theme
    db.commit()
    db.refresh(settings)
    return settings
