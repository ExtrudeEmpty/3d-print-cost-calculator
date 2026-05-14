from sqlalchemy import (
    Column, Integer, String, Numeric, Date, Boolean, Text,
    DateTime, ForeignKey, CheckConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class Printer(Base):
    __tablename__ = "printers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    purchase_price = Column(Numeric(10, 2), nullable=False)
    purchase_date = Column(Date, nullable=False)
    max_wattage = Column(Integer, nullable=False, default=300)
    has_heated_bed = Column(Boolean, default=False, nullable=False)
    max_wattage_bed = Column(Integer, nullable=False, default=0)
    has_heated_chamber = Column(Boolean, default=False, nullable=False)
    chamber_wattage = Column(Integer, nullable=False, default=0)
    chamber_power_factor = Column(Numeric(4, 3), nullable=False, default=1.000)
    power_factor = Column(Numeric(4, 3), nullable=False, default=1.000)
    expected_lifetime_hours = Column(Integer, nullable=False)
    preferred_dryer_id = Column(Integer, ForeignKey("dryers.id"), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    orders = relationship("Order", back_populates="printer")
    maintenance_records = relationship("Maintenance", back_populates="printer")
    calibrations = relationship("PrinterMaterialCalibration", back_populates="printer", cascade="all, delete-orphan")
    preferred_dryer = relationship("Dryer")

class FilamentType(Base):
    __tablename__ = "filament_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)
    
    # Technical Parameters
    min_nozzle_temp = Column(Integer, default=200)
    max_nozzle_temp = Column(Integer, default=220)
    min_bed_temp = Column(Integer, default=60)
    chamber_temp_min = Column(Integer, default=0)
    needs_chamber = Column(Boolean, default=False)
    
    # Dryer Parameters
    needs_dryer = Column(Boolean, default=False)
    dryer_temp = Column(Integer, default=50)
    dryer_hours = Column(Numeric(4, 1), default=4.0)
    dryer_mode_default = Column(String(20), default="none") # none, pre_only, during_only, pre_and_during
    default_density = Column(Numeric(4, 2), default=1.24)

    materials = relationship("Material", back_populates="filament_type")
    printer_calibrations = relationship("PrinterMaterialCalibration", back_populates="filament_type", cascade="all, delete-orphan")
    dryer_calibrations = relationship("DryerMaterialCalibration", back_populates="filament_type", cascade="all, delete-orphan")

class PrinterMaterialCalibration(Base):
    __tablename__ = "printer_material_calibration"

    printer_id = Column(Integer, ForeignKey("printers.id", ondelete="CASCADE"), primary_key=True)
    filament_type_id = Column(Integer, ForeignKey("filament_types.id", ondelete="CASCADE"), primary_key=True)
    power_factor = Column(Numeric(4, 3), nullable=False)
    measured_at = Column(DateTime(timezone=True), server_default=func.now())

    printer = relationship("Printer", back_populates="calibrations")
    filament_type = relationship("FilamentType", back_populates="printer_calibrations")


class Dryer(Base):
    __tablename__ = "dryers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    max_wattage = Column(Integer, nullable=False, default=50)
    power_factor = Column(Numeric(4, 3), nullable=False, default=1.000)
    has_ams = Column(Boolean, default=False, nullable=False)
    ams_wattage = Column(Integer, nullable=False, default=0)
    ams_power_factor = Column(Numeric(4, 3), nullable=False, default=1.000)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    orders = relationship("Order", back_populates="dryer")
    calibrations = relationship("DryerMaterialCalibration", back_populates="dryer", cascade="all, delete-orphan")


class DryerMaterialCalibration(Base):
    __tablename__ = "dryer_material_calibration"

    dryer_id = Column(Integer, ForeignKey("dryers.id", ondelete="CASCADE"), primary_key=True)
    filament_type_id = Column(Integer, ForeignKey("filament_types.id", ondelete="CASCADE"), primary_key=True)
    power_factor = Column(Numeric(4, 3), nullable=False)
    measured_at = Column(DateTime(timezone=True), server_default=func.now())

    dryer = relationship("Dryer", back_populates="calibrations")
    filament_type = relationship("FilamentType", back_populates="dryer_calibrations")


class Material(Base):
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    filament_type_id = Column(Integer, ForeignKey("filament_types.id"), nullable=True)
    price_per_kg = Column(Numeric(8, 2), nullable=False)
    density_g_per_cm3 = Column(Numeric(4, 2), default=1.24)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    filament_type = relationship("FilamentType", back_populates="materials")
    order_materials = relationship("OrderMaterial", back_populates="material")

class OrderMaterial(Base):
    __tablename__ = "order_materials"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    material_id = Column(Integer, ForeignKey("materials.id", ondelete="CASCADE"), nullable=False)
    filament_used_g = Column(Numeric(8, 2), nullable=False)

    order = relationship("Order", back_populates="materials")
    material = relationship("Material", back_populates="order_materials")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, server_default=func.current_date())
    printer_id = Column(Integer, ForeignKey("printers.id"), nullable=False)
    dryer_id = Column(Integer, ForeignKey("dryers.id"), nullable=True)
    dryer_mode = Column(String(20), default="none")
    dryer_pre_hours = Column(Numeric(6, 2), default=0.00)
    use_dryer_ams = Column(Boolean, default=False, nullable=False)
    print_time_hours = Column(Numeric(6, 2), nullable=False)
    supports = Column(Boolean, default=False)
    postprocessing_minutes = Column(Integer, default=0)
    material_cost = Column(Numeric(10, 2), nullable=False)
    electricity_cost = Column(Numeric(10, 2), nullable=False)
    depreciation_cost = Column(Numeric(10, 2), nullable=False)
    labor_cost = Column(Numeric(10, 2), nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)
    profit = Column(Numeric(10, 2), nullable=False)
    maintenance_cost = Column(Numeric(10, 2), nullable=False, default=0)
    other_costs = Column(Numeric(10, 2), nullable=False, default=0)
    selling_price = Column(Numeric(10, 2), nullable=True)
    customer_type = Column(String(20), nullable=False, default="business")
    customer_name = Column(String(200), nullable=True)
    notes = Column(Text, nullable=True)
    batch_quantity = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    use_heated_chamber = Column(Boolean, default=False, nullable=False)

    printer = relationship("Printer", back_populates="orders")
    dryer = relationship("Dryer", back_populates="orders")
    materials = relationship("OrderMaterial", back_populates="order", cascade="all, delete-orphan")


class Maintenance(Base):
    __tablename__ = "maintenance"

    id = Column(Integer, primary_key=True, index=True)
    printer_id = Column(Integer, ForeignKey("printers.id"), nullable=False)
    date = Column(Date, nullable=False, server_default=func.current_date())
    part_type = Column(String(50), nullable=False)
    cost = Column(Numeric(8, 2), nullable=False)  # This will be part_cost
    labor_hours = Column(Numeric(6, 2), nullable=False, default=0)
    hourly_rate_type = Column(String(20), nullable=False, default="private")
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    printer = relationship("Printer", back_populates="maintenance_records")


class Settings(Base):
    __tablename__ = "settings"
    __table_args__ = (
        CheckConstraint("id = 1", name="singleton_settings"),
    )

    id = Column(Integer, primary_key=True, default=1)
    electricity_price_per_kwh = Column(Numeric(6, 4), nullable=False, default=0.35)
    hourly_labor_rate = Column(Numeric(8, 2), nullable=False, default=15.00)
    maintenance_cost_per_hour = Column(Numeric(6, 2), nullable=False, default=0.50)
    margin_business = Column(Numeric(5, 2), nullable=False, default=40.00)
    margin_friends = Column(Numeric(5, 2), nullable=False, default=15.00)
    margin_private = Column(Numeric(5, 2), nullable=False, default=0.00)
    labor_factor_business = Column(Numeric(3, 2), nullable=False, default=1.00)
    labor_factor_friends = Column(Numeric(3, 2), nullable=False, default=0.50)
    labor_factor_private = Column(Numeric(3, 2), nullable=False, default=0.00)
    language = Column(String(10), nullable=False, default="en")
    number_format_locale = Column(String(10), nullable=False, default="de-DE")
    date_format = Column(String(20), nullable=False, default="DD.MM.YYYY")
    currency_symbol = Column(String(5), nullable=False, default="€")
    currency_position = Column(String(20), nullable=False, default="end_with_space")
    theme = Column(String(10), nullable=False, default="dark")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
