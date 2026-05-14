import math
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from models import Order, Printer, Material, Settings, Dryer, PrinterMaterialCalibration, DryerMaterialCalibration, OrderMaterial
from schemas import (
    CalculateRequest, CalculateResponse, CostBreakdown,
    OrderCreate, OrderResponse, OrderListResponse, OrderMaterialResponse
)
from calculator import calculate_price, parse_time_string

router = APIRouter(prefix="/api", tags=["orders"])


def _get_settings(db: Session) -> Settings:
    settings = db.query(Settings).filter(Settings.id == 1).first()
    if not settings:
        raise HTTPException(status_code=500, detail="Einstellungen nicht konfiguriert")
    return settings


MARGIN_MAP = {
    "business": "margin_business",
    "friends": "margin_friends",
    "private": "margin_private",
}

LABOR_FACTOR_MAP = {
    "business": "labor_factor_business",
    "friends": "labor_factor_friends",
    "private": "labor_factor_private",
}


def _get_tier_settings(settings: Settings, customer_type: str) -> tuple[float, float]:
    """Resolve margin and labor_factor for a customer type."""
    margin_attr = MARGIN_MAP.get(customer_type)
    factor_attr = LABOR_FACTOR_MAP.get(customer_type)
    if not margin_attr:
        raise HTTPException(status_code=400, detail=f"Ungültiger Kundentyp: {customer_type}")
    return float(getattr(settings, margin_attr)), float(getattr(settings, factor_attr))


def _perform_calculation(
    printer: Printer,
    base_material: Material,
    settings: Settings,
    total_material_cost: float,
    print_time_hours: float,
    postprocessing_minutes: int,
    customer_type: str = "business",
    other_costs: float = 0.0,
    dryer: Dryer = None,
    dryer_mode: str = "none",
    dryer_pre_hours: float = 0.0,
    use_dryer_ams: bool = False,
    use_heated_chamber: bool = False,
    db: Session = None,
) -> dict:
    margin, labor_factor = _get_tier_settings(settings, customer_type)
    
    # Material-specific printer power factor
    printer_pf = float(printer.power_factor)
    if db and base_material.filament_type_id:
        p_calib = db.query(PrinterMaterialCalibration).filter_by(printer_id=printer.id, filament_type_id=base_material.filament_type_id).first()
        if p_calib:
            printer_pf = float(p_calib.power_factor)

    # Material-specific dryer power factor
    dryer_max_wattage = dryer.max_wattage if dryer else 0
    
    total_dryer_hours = 0.0
    if dryer and dryer_mode != "none":
        if dryer_mode == "pre_only":
            total_dryer_hours = dryer_pre_hours
        elif dryer_mode == "during_only":
            total_dryer_hours = print_time_hours
        elif dryer_mode == "pre_and_during":
            total_dryer_hours = print_time_hours + dryer_pre_hours

    dryer_pf = 0.0
    if dryer and total_dryer_hours > 0:
        dryer_pf = float(dryer.power_factor)
        if db and base_material.filament_type_id:
            d_calib = db.query(DryerMaterialCalibration).filter_by(dryer_id=dryer.id, filament_type_id=base_material.filament_type_id).first()
            if d_calib:
                dryer_pf = float(d_calib.power_factor)

    total_printer_wattage = printer.max_wattage
    if printer.has_heated_bed:
        total_printer_wattage += printer.max_wattage_bed
    if printer.has_heated_chamber and use_heated_chamber:
        total_printer_wattage += printer.chamber_wattage

    result = calculate_price(
        total_material_cost=total_material_cost,
        print_time_hours=print_time_hours,
        postprocessing_minutes=postprocessing_minutes,
        printer_max_wattage=total_printer_wattage,
        printer_power_factor=printer_pf,
        printer_purchase_price=float(printer.purchase_price),
        printer_expected_lifetime_hours=printer.expected_lifetime_hours,
        electricity_price_per_kwh=float(settings.electricity_price_per_kwh),
        hourly_labor_rate=float(settings.hourly_labor_rate),
        maintenance_cost_per_hour=float(settings.maintenance_cost_per_hour),
        profit_margin_percent=margin,
        labor_factor=labor_factor,
        other_costs=other_costs,
        dryer_max_wattage=dryer_max_wattage,
        dryer_power_factor=dryer_pf,
        total_dryer_hours=total_dryer_hours,
        dryer_ams_wattage=dryer.ams_wattage if dryer and dryer.has_ams else 0,
        dryer_ams_pf=float(dryer.ams_power_factor) if dryer and dryer.has_ams else 0.0,
        use_dryer_ams=use_dryer_ams if dryer and dryer.has_ams else False,
    )
    return result


def _generate_warnings(printer: Printer, material: Material, dryer_mode: str, use_heated_chamber: bool) -> list[str]:
    warnings = []
    f_type = material.filament_type
    if not f_type:
        return warnings
    
    if f_type.needs_chamber:
        chamber_temp_str = f" ({f_type.chamber_temp_min}°C)" if f_type.chamber_temp_min > 0 else ""
        if not use_heated_chamber:
            warnings.append(f"Material '{f_type.name}' empfiehlt eine Bauraumheizung{chamber_temp_str}, diese ist jedoch deaktiviert.")
        elif not printer.has_heated_chamber:
            warnings.append(f"Material '{f_type.name}' benötigt eine Bauraumheizung{chamber_temp_str}, aber der Drucker '{printer.name}' besitzt keine.")
        
    if f_type.needs_dryer and dryer_mode == "none":
        warnings.append(f"Material '{f_type.name}' sollte vor/während des Drucks getrocknet werden.")
        
    return warnings


@router.post("/calculate", response_model=CalculateResponse)
def calculate(data: CalculateRequest, db: Session = Depends(get_db)):
    # Parse time fields if they are strings
    try:
        data.print_time_hours = parse_time_string(data.print_time_hours, "hours")
        data.dryer_pre_hours = parse_time_string(data.dryer_pre_hours, "hours")
        data.postprocessing_minutes = int(parse_time_string(data.postprocessing_minutes, "minutes"))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    printer = db.query(Printer).filter(Printer.id == data.printer_id).first()
    if not printer:
        raise HTTPException(status_code=404, detail="Drucker nicht gefunden")

    if not data.materials:
        raise HTTPException(status_code=400, detail="Kein Material ausgewählt")

    total_material_cost = 0.0
    base_material = None
    
    for idx, mat_item in enumerate(data.materials):
        mat = db.query(Material).filter(Material.id == mat_item.material_id).first()
        if not mat:
            raise HTTPException(status_code=404, detail=f"Material mit ID {mat_item.material_id} nicht gefunden")
        if idx == 0:
            base_material = mat
        
        cost_for_this = (mat_item.filament_used_g / 1000) * float(mat.price_per_kg)
        total_material_cost += cost_for_this

    settings = _get_settings(db)
    
    dryer = None
    if data.dryer_id:
        dryer = db.query(Dryer).filter(Dryer.id == data.dryer_id).first()
        if not dryer:
            raise HTTPException(status_code=404, detail="Trockner nicht gefunden")

    result = _perform_calculation(
        printer, base_material, settings,
        total_material_cost, data.print_time_hours, data.postprocessing_minutes,
        data.customer_type, data.other_costs, dryer, data.dryer_mode, data.dryer_pre_hours, data.use_dryer_ams, data.use_heated_chamber, db
    )

    warnings = _generate_warnings(printer, base_material, data.dryer_mode, data.use_heated_chamber)

    return CalculateResponse(
        material_cost=result.material_cost,
        electricity_cost=result.electricity_cost,
        depreciation_cost=result.depreciation_cost,
        maintenance_cost=result.maintenance_cost,
        labor_cost=result.labor_cost,
        other_costs=result.other_costs,
        subtotal=result.subtotal,
        profit_margin_percent=result.profit_margin_percent,
        profit=result.profit,
        total_price=result.total_price,
        breakdown=CostBreakdown(
            material_price_per_kg=float(base_material.price_per_kg),
            electricity_price_per_kwh=float(settings.electricity_price_per_kwh),
            printer_depreciation_per_hour=round(
                float(printer.purchase_price) / printer.expected_lifetime_hours, 4
            ),
            maintenance_cost_per_hour=float(settings.maintenance_cost_per_hour),
            labor_rate_per_hour=float(settings.hourly_labor_rate),
            labor_factor=_get_tier_settings(settings, data.customer_type)[1],
            warnings=warnings,
        ),
        warnings=warnings,
    )


@router.post("/orders", response_model=OrderResponse, status_code=201)
def create_order(data: OrderCreate, db: Session = Depends(get_db)):
    # Parse time fields if they are strings
    try:
        data.print_time_hours = parse_time_string(data.print_time_hours, "hours")
        data.dryer_pre_hours = parse_time_string(data.dryer_pre_hours, "hours")
        data.postprocessing_minutes = int(parse_time_string(data.postprocessing_minutes, "minutes"))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    printer = db.query(Printer).filter(Printer.id == data.printer_id).first()
    if not printer:
        raise HTTPException(status_code=404, detail="Drucker nicht gefunden")

    if not data.materials:
        raise HTTPException(status_code=400, detail="Kein Material ausgewählt")

    total_material_cost = 0.0
    base_material = None
    
    for idx, mat_item in enumerate(data.materials):
        mat = db.query(Material).filter(Material.id == mat_item.material_id).first()
        if not mat:
            raise HTTPException(status_code=404, detail=f"Material mit ID {mat_item.material_id} nicht gefunden")
        if idx == 0:
            base_material = mat
        
        cost_for_this = (mat_item.filament_used_g / 1000) * float(mat.price_per_kg)
        total_material_cost += cost_for_this

    settings = _get_settings(db)

    dryer = None
    if data.dryer_id:
        dryer = db.query(Dryer).filter(Dryer.id == data.dryer_id).first()
        if not dryer:
            raise HTTPException(status_code=404, detail="Trockner nicht gefunden")

    result = _perform_calculation(
        printer, base_material, settings,
        total_material_cost, data.print_time_hours, data.postprocessing_minutes,
        data.customer_type, data.other_costs, dryer, data.dryer_mode, data.dryer_pre_hours, data.use_dryer_ams, data.use_heated_chamber, db
    )

    order = Order(
        printer_id=data.printer_id,
        dryer_id=data.dryer_id,
        dryer_mode=data.dryer_mode,
        dryer_pre_hours=data.dryer_pre_hours,
        use_dryer_ams=data.use_dryer_ams,
        print_time_hours=data.print_time_hours,
        supports=data.supports,
        postprocessing_minutes=data.postprocessing_minutes,
        material_cost=result.material_cost,
        electricity_cost=result.electricity_cost,
        depreciation_cost=result.depreciation_cost,
        maintenance_cost=result.maintenance_cost,
        other_costs=data.other_costs,
        labor_cost=result.labor_cost,
        total_price=result.total_price,
        profit=result.profit,
        selling_price=data.selling_price if data.selling_price is not None else result.total_price,
        customer_type=data.customer_type,
        customer_name=data.customer_name,
        notes=data.notes,
        use_heated_chamber=data.use_heated_chamber,
        batch_quantity=data.batch_quantity,
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    # Add materials to order
    for mat_item in data.materials:
        om = OrderMaterial(
            order_id=order.id,
            material_id=mat_item.material_id,
            filament_used_g=mat_item.filament_used_g
        )
        db.add(om)
    db.commit()
    db.refresh(order)

    return OrderResponse(
        id=order.id,
        date=order.date,
        printer_id=order.printer_id,
        printer_name=printer.name,
        materials=[OrderMaterialResponse(
            material_id=om.material_id,
            material_name=om.material.name,
            filament_used_g=float(om.filament_used_g)
        ) for om in order.materials],
        dryer_id=order.dryer_id,
        dryer_mode=order.dryer_mode,
        dryer_pre_hours=float(order.dryer_pre_hours),
        use_dryer_ams=order.use_dryer_ams,
        print_time_hours=float(order.print_time_hours),
        supports=order.supports,
        postprocessing_minutes=order.postprocessing_minutes,
        material_cost=float(order.material_cost),
        electricity_cost=float(order.electricity_cost),
        depreciation_cost=float(order.depreciation_cost),
        maintenance_cost=float(order.maintenance_cost),
        other_costs=float(order.other_costs),
        labor_cost=float(order.labor_cost),
        total_price=float(order.total_price),
        profit=float(order.profit),
        selling_price=float(order.selling_price) if order.selling_price else None,
        customer_type=order.customer_type,
        customer_name=order.customer_name,
        notes=order.notes,
        use_heated_chamber=order.use_heated_chamber,
        batch_quantity=order.batch_quantity,
    )


@router.get("/orders", response_model=OrderListResponse)
def list_orders(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    total = db.query(Order).count()
    pages = math.ceil(total / per_page) if total > 0 else 1
    offset = (page - 1) * per_page

    orders = (
        db.query(Order)
        .order_by(Order.date.desc(), Order.id.desc())
        .offset(offset)
        .limit(per_page)
        .all()
    )

    items = []
    for o in orders:
        items.append(OrderResponse(
            id=o.id,
            date=o.date,
            printer_id=o.printer_id,
            printer_name=o.printer.name,
            materials=[OrderMaterialResponse(
                material_id=om.material_id,
                material_name=om.material.name,
                filament_used_g=float(om.filament_used_g)
            ) for om in o.materials],
            dryer_id=o.dryer_id,
            dryer_mode=o.dryer_mode,
            dryer_pre_hours=float(o.dryer_pre_hours),
            use_dryer_ams=o.use_dryer_ams,
            print_time_hours=float(o.print_time_hours),
            supports=o.supports,
            postprocessing_minutes=o.postprocessing_minutes,
            material_cost=float(o.material_cost),
            electricity_cost=float(o.electricity_cost),
            depreciation_cost=float(o.depreciation_cost),
            maintenance_cost=float(o.maintenance_cost),
            other_costs=float(o.other_costs),
            labor_cost=float(o.labor_cost),
            total_price=float(o.total_price),
            profit=float(o.profit),
            selling_price=float(o.selling_price) if o.selling_price else None,
            customer_type=o.customer_type,
            customer_name=o.customer_name,
            notes=o.notes,
            use_heated_chamber=o.use_heated_chamber,
            batch_quantity=o.batch_quantity,
        ))

    return OrderListResponse(
        items=items,
        total=total,
        page=page,
        per_page=per_page,
        pages=pages,
    )


@router.get("/orders/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Auftrag nicht gefunden")

    return OrderResponse(
        id=order.id,
        date=order.date,
        printer_id=order.printer_id,
        printer_name=order.printer.name,
        materials=[OrderMaterialResponse(
            material_id=om.material_id,
            material_name=om.material.name,
            filament_used_g=float(om.filament_used_g)
        ) for om in order.materials],
        dryer_id=order.dryer_id,
        dryer_mode=order.dryer_mode,
        dryer_pre_hours=float(order.dryer_pre_hours),
        use_dryer_ams=order.use_dryer_ams,
        print_time_hours=float(order.print_time_hours),
        supports=order.supports,
        postprocessing_minutes=order.postprocessing_minutes,
        material_cost=float(order.material_cost),
        electricity_cost=float(order.electricity_cost),
        depreciation_cost=float(order.depreciation_cost),
        maintenance_cost=float(order.maintenance_cost),
        other_costs=float(order.other_costs),
        labor_cost=float(order.labor_cost),
        total_price=float(order.total_price),
        profit=float(order.profit),
        selling_price=float(order.selling_price) if order.selling_price else None,
        customer_type=order.customer_type,
        customer_name=order.customer_name,
        notes=order.notes,
        use_heated_chamber=order.use_heated_chamber,
        batch_quantity=order.batch_quantity,
    )


@router.delete("/orders/{order_id}", status_code=204)
def delete_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Auftrag nicht gefunden")
    db.delete(order)
    db.commit()
    return None
