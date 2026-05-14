from pydantic import BaseModel, Field
from typing import Optional, Union
from datetime import date, datetime


# ─── Printer ──────────────────────────────────────────────────────

class PrinterCreate(BaseModel):
    name: str = Field(..., max_length=100)
    purchase_price: float = Field(..., gt=0)
    purchase_date: date
    max_wattage: int = Field(300, gt=0)
    has_heated_bed: bool = False
    max_wattage_bed: int = Field(0, ge=0)
    has_heated_chamber: bool = False
    chamber_wattage: int = Field(0, ge=0)
    chamber_power_factor: float = Field(1.0, ge=0.0, le=1.0)
    power_factor: float = Field(1.0, ge=0.0, le=1.0)
    expected_lifetime_hours: Union[int, float, str] = Field(..., gt=0)
    preferred_dryer_id: Optional[int] = None


class PrinterUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    purchase_price: Optional[float] = Field(None, gt=0)
    purchase_date: Optional[date] = None
    max_wattage: Optional[int] = Field(None, gt=0)
    has_heated_bed: Optional[bool] = None
    max_wattage_bed: Optional[int] = Field(None, ge=0)
    has_heated_chamber: Optional[bool] = None
    chamber_wattage: Optional[int] = Field(None, ge=0)
    chamber_power_factor: Optional[float] = Field(None, ge=0.0, le=1.0)
    power_factor: Optional[float] = Field(None, ge=0.0, le=1.0)
    expected_lifetime_hours: Optional[Union[int, float, str]] = Field(None, gt=0)
    preferred_dryer_id: Optional[int] = None


class PrinterResponse(BaseModel):
    id: int
    name: str
    purchase_price: float
    purchase_date: date
    max_wattage: int
    has_heated_bed: bool
    max_wattage_bed: int
    has_heated_chamber: bool
    chamber_wattage: int
    chamber_power_factor: float
    power_factor: float
    expected_lifetime_hours: int
    is_active: bool
    preferred_dryer_id: Optional[int] = None

    model_config = {"from_attributes": True}


# ─── Dryer ────────────────────────────────────────────────────────

class DryerCreate(BaseModel):
    name: str = Field(..., max_length=100)
    max_wattage: int = Field(50, gt=0)
    power_factor: float = Field(1.0, ge=0.0, le=1.0)
    has_ams: bool = False
    ams_wattage: int = Field(0, ge=0)
class DryerUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    max_wattage: Optional[int] = Field(None, gt=0)
    power_factor: Optional[float] = Field(None, ge=0.0, le=1.0)
    has_ams: Optional[bool] = None
    ams_wattage: Optional[int] = Field(None, ge=0)
    ams_power_factor: Optional[float] = Field(None, ge=0.0, le=1.0)


class DryerResponse(BaseModel):
    id: int
    name: str
    max_wattage: int
    power_factor: float
    has_ams: bool
    ams_wattage: int
    ams_power_factor: float
    is_active: bool

    model_config = {"from_attributes": True}


# ─── Filament Type ────────────────────────────────────────────────

class FilamentTypeCreate(BaseModel):
    name: str = Field(..., max_length=50)
    min_nozzle_temp: int = 200
    max_nozzle_temp: int = 220
    min_bed_temp: int = 60
    chamber_temp_min: int = 0
    needs_chamber: bool = False
    needs_dryer: bool = False
    dryer_temp: int = 50
    dryer_hours: Union[float, str] = 4.0
    dryer_mode_default: str = Field("none", pattern="^(none|pre_only|during_only|pre_and_during)$")
    default_density: float = 1.24


class FilamentTypeUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=50)
    min_nozzle_temp: Optional[int] = None
    max_nozzle_temp: Optional[int] = None
    min_bed_temp: Optional[int] = None
    chamber_temp_min: Optional[int] = None
    needs_chamber: Optional[bool] = None
    needs_dryer: Optional[bool] = None
    dryer_temp: Optional[int] = None
    dryer_hours: Optional[Union[float, str]] = None
    dryer_mode_default: Optional[str] = Field(None, pattern="^(none|pre_only|during_only|pre_and_during)$")
    default_density: Optional[float] = None


class FilamentTypeResponse(BaseModel):
    id: int
    name: str
    min_nozzle_temp: int
    max_nozzle_temp: int
    min_bed_temp: int
    chamber_temp_min: int
    needs_chamber: bool
    needs_dryer: bool
    dryer_temp: int
    dryer_hours: float
    dryer_mode_default: str
    default_density: float

    model_config = {"from_attributes": True}

# ─── Calibration ──────────────────────────────────────────────────

class CalibrationCreate(BaseModel):
    filament_type_id: int
    power_factor: float = Field(..., ge=0.0, le=1.0)


class CalibrationResponse(BaseModel):
    filament_type_id: int
    filament_type_name: str
    power_factor: float
    measured_at: datetime

    model_config = {"from_attributes": True}


# ─── Material ─────────────────────────────────────────────────────

class MaterialCreate(BaseModel):
    name: str = Field(..., max_length=100)
    filament_type_id: Optional[int] = None
    price_per_kg: float = Field(..., gt=0)
    density_g_per_cm3: Optional[float] = Field(1.24, gt=0)


class MaterialUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    filament_type_id: Optional[int] = None
    price_per_kg: Optional[float] = Field(None, gt=0)
    density_g_per_cm3: Optional[float] = Field(None, gt=0)


class MaterialResponse(BaseModel):
    id: int
    name: str
    filament_type_id: Optional[int]
    filament_type_name: Optional[str] = None
    price_per_kg: float
    density_g_per_cm3: float
    is_active: bool

    model_config = {"from_attributes": True}


class OrderMaterialItem(BaseModel):
    material_id: int
    filament_used_g: float = Field(..., gt=0)

class OrderMaterialResponse(BaseModel):
    material_id: int
    material_name: str
    filament_used_g: float

# ─── Calculation ──────────────────────────────────────────────────

class CalculateRequest(BaseModel):
    printer_id: int
    materials: list[OrderMaterialItem]
    dryer_id: Optional[int] = None
    dryer_mode: str = Field("none", pattern="^(none|pre_only|during_only|pre_and_during)$")
    dryer_pre_hours: Union[float, str] = Field(0.0, ge=0.0)
    use_dryer_ams: bool = False
    print_time_hours: Union[float, str] = Field(..., gt=0)
    supports: bool = False
    postprocessing_minutes: Union[int, float, str] = Field(0, ge=0)
    customer_type: str = Field("business", pattern="^(business|friends|private)$")
    other_costs: float = Field(0, ge=0)
    use_heated_chamber: bool = False


class CostBreakdown(BaseModel):
    material_price_per_kg: float
    electricity_price_per_kwh: float
    printer_depreciation_per_hour: float
    maintenance_cost_per_hour: float
    labor_rate_per_hour: float
    labor_factor: float
    warnings: list[str] = []


class CalculateResponse(BaseModel):
    material_cost: float
    electricity_cost: float
    depreciation_cost: float
    maintenance_cost: float
    labor_cost: float
    other_costs: float
    subtotal: float
    profit_margin_percent: float
    profit: float
    total_price: float
    breakdown: CostBreakdown
    warnings: list[str] = []


# ─── Order ────────────────────────────────────────────────────────

class OrderCreate(BaseModel):
    printer_id: int
    materials: list[OrderMaterialItem]
    dryer_id: Optional[int] = None
    dryer_mode: str = Field("none", pattern="^(none|pre_only|during_only|pre_and_during)$")
    dryer_pre_hours: Union[float, str] = Field(0.0, ge=0.0)
    use_dryer_ams: bool = False
    print_time_hours: Union[float, str] = Field(..., gt=0)
    supports: bool = False
    postprocessing_minutes: Union[int, float, str] = Field(0, ge=0)
    customer_type: str = Field("business", pattern="^(business|friends|private)$")
    other_costs: float = Field(0, ge=0)
    selling_price: Optional[float] = None
    customer_name: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = None
    use_heated_chamber: bool = False
    batch_quantity: int = Field(1, ge=1)


class OrderResponse(BaseModel):
    id: int
    date: date
    printer_id: int
    printer_name: str
    materials: list[OrderMaterialResponse]
    dryer_id: Optional[int]
    dryer_mode: str
    dryer_pre_hours: float
    use_dryer_ams: bool
    print_time_hours: float
    supports: bool
    postprocessing_minutes: int
    material_cost: float
    electricity_cost: float
    depreciation_cost: float
    maintenance_cost: float
    labor_cost: float
    other_costs: float
    total_price: float
    profit: float
    selling_price: Optional[float]
    customer_type: str
    customer_name: Optional[str]
    notes: Optional[str]
    use_heated_chamber: bool
    batch_quantity: int = 1


class OrderListResponse(BaseModel):
    items: list[OrderResponse]
    total: int
    page: int
    per_page: int
    pages: int


# ─── Maintenance ──────────────────────────────────────────────────

class MaintenanceCreate(BaseModel):
    printer_id: int
    date: Optional[date] = None
    part_type: str = Field(..., max_length=50)
    cost: float = Field(..., ge=0)
    labor_hours: float = Field(0, ge=0)
    hourly_rate_type: str = Field("private", pattern="^(private|friends|business)$")
    notes: Optional[str] = None


class MaintenanceResponse(BaseModel):
    id: int
    printer_id: int
    printer_name: str
    date: date
    part_type: str
    cost: float
    labor_hours: float = 0
    hourly_rate_type: str = "private"
    total_cost: float = 0
    notes: Optional[str]

    model_config = {"from_attributes": True}


# ─── Settings ─────────────────────────────────────────────────────

class SettingsResponse(BaseModel):
    electricity_price_per_kwh: float
    hourly_labor_rate: float
    maintenance_cost_per_hour: float
    margin_business: float
    margin_friends: float
    margin_private: float
    labor_factor_business: float
    labor_factor_friends: float
    labor_factor_private: float
    language: str
    number_format_locale: str
    date_format: str
    currency_symbol: str
    currency_position: str
    theme: str

    model_config = {"from_attributes": True}


class SettingsUpdate(BaseModel):
    electricity_price_per_kwh: Optional[float] = Field(None, gt=0)
    hourly_labor_rate: Optional[float] = Field(None, ge=0)
    maintenance_cost_per_hour: Optional[float] = Field(None, ge=0)
    margin_business: Optional[float] = Field(None, ge=0)
    margin_friends: Optional[float] = Field(None, ge=0)
    margin_private: Optional[float] = Field(None, ge=0)
    labor_factor_business: Optional[float] = Field(None, ge=0, le=1)
    labor_factor_friends: Optional[float] = Field(None, ge=0, le=1)
    labor_factor_private: Optional[float] = Field(None, ge=0, le=1)
    language: Optional[str] = Field(None, max_length=10)
    number_format_locale: Optional[str] = Field(None, max_length=10)
    date_format: Optional[str] = Field(None, max_length=20)
    currency_symbol: Optional[str] = Field(None, max_length=5)
    currency_position: Optional[str] = Field(None, max_length=20)
    theme: Optional[str] = Field(None, max_length=10)

class LanguageUpdate(BaseModel):
    language: str = Field(..., max_length=10)

class ThemeUpdate(BaseModel):
    theme: str = Field(..., min_length=4, max_length=10)

class FormattingUpdate(BaseModel):
    language: Optional[str] = Field(None, max_length=10)
    number_format_locale: Optional[str] = Field(None, max_length=10)
    date_format: Optional[str] = Field(None, max_length=20)
    currency_symbol: Optional[str] = Field(None, max_length=5)
    currency_position: Optional[str] = Field(None, max_length=20)

class PreferenceResponse(BaseModel):
    language: str
    number_format_locale: str
    date_format: str
    currency_symbol: str
    currency_position: str
    theme: str

    model_config = {"from_attributes": True}


# ─── Dashboard ────────────────────────────────────────────────────

class PrinterStats(BaseModel):
    id: int
    name: str
    total_print_hours: float
    total_revenue: float
    total_maintenance_cost: float
    amortization_percent: float
    is_amortized: bool


class MaintenanceAlert(BaseModel):
    printer_id: int
    printer_name: str
    hours_since_last_maintenance: float
    message: str


class TopMaterial(BaseModel):
    name: str
    total_used_g: float
    order_count: int


class DashboardStats(BaseModel):
    total_orders: int
    total_revenue: float
    total_profit: float
    avg_profit_margin_percent: float
    orders_this_month: int
    profit_this_month: float
    printers: list[PrinterStats]
    maintenance_alerts: list[MaintenanceAlert]
    top_materials: list[TopMaterial]
