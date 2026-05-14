from datetime import date, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, extract

from database import get_db
from models import Order, Printer, Material, Maintenance, OrderMaterial
from schemas import DashboardStats, PrinterStats, MaintenanceAlert, TopMaterial

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

# Alert threshold: hours since last maintenance
MAINTENANCE_ALERT_HOURS = 200


@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    today = date.today()
    current_month_start = today.replace(day=1)

    # ── Overall stats ──
    total_orders = db.query(Order).count()
    total_revenue = db.query(func.coalesce(func.sum(Order.total_price), 0)).scalar()
    total_profit = db.query(func.coalesce(func.sum(Order.profit), 0)).scalar()

    avg_margin = 0.0
    if total_revenue and float(total_revenue) > 0:
        avg_margin = round(float(total_profit) / float(total_revenue) * 100, 1)

    # ── This month ──
    month_orders = (
        db.query(Order)
        .filter(Order.date >= current_month_start)
        .count()
    )
    month_profit = (
        db.query(func.coalesce(func.sum(Order.profit), 0))
        .filter(Order.date >= current_month_start)
        .scalar()
    )

    # ── Printer stats ──
    printers = db.query(Printer).filter(Printer.is_active == True).all()
    printer_stats = []
    maintenance_alerts = []

    for p in printers:
        # Total print hours and revenue from orders
        p_hours = (
            db.query(func.coalesce(func.sum(Order.print_time_hours), 0))
            .filter(Order.printer_id == p.id)
            .scalar()
        )
        p_revenue = (
            db.query(func.coalesce(func.sum(Order.total_price), 0))
            .filter(Order.printer_id == p.id)
            .scalar()
        )
        p_maintenance = (
            db.query(func.coalesce(func.sum(Maintenance.cost), 0))
            .filter(Maintenance.printer_id == p.id)
            .scalar()
        )

        purchase_price = float(p.purchase_price)
        revenue_f = float(p_revenue)
        maint_f = float(p_maintenance)
        amort = round((revenue_f - maint_f) / purchase_price * 100, 1) if purchase_price > 0 else 0

        printer_stats.append(PrinterStats(
            id=p.id,
            name=p.name,
            total_print_hours=round(float(p_hours), 1),
            total_revenue=round(revenue_f, 2),
            total_maintenance_cost=round(maint_f, 2),
            amortization_percent=amort,
            is_amortized=amort >= 100,
        ))

        # Maintenance alerts
        last_maint = (
            db.query(Maintenance)
            .filter(Maintenance.printer_id == p.id)
            .order_by(Maintenance.date.desc())
            .first()
        )

        hours_total = float(p_hours)
        if last_maint:
            # Hours printed since last maintenance (approximation)
            hours_since = (
                db.query(func.coalesce(func.sum(Order.print_time_hours), 0))
                .filter(Order.printer_id == p.id, Order.date > last_maint.date)
                .scalar()
            )
            hours_since_f = float(hours_since)
        else:
            hours_since_f = hours_total

        if hours_since_f >= MAINTENANCE_ALERT_HOURS:
            maintenance_alerts.append(MaintenanceAlert(
                printer_id=p.id,
                printer_name=p.name,
                hours_since_last_maintenance=round(hours_since_f, 1),
                message=f"Letzte Wartung vor {round(hours_since_f)}h — Wartung empfohlen",
            ))

    # ── Top materials ──
    top_mats = (
        db.query(
            Material.name,
            func.coalesce(func.sum(OrderMaterial.filament_used_g), 0).label("total_g"),
            func.count(func.distinct(OrderMaterial.order_id)).label("order_count"),
        )
        .join(OrderMaterial, OrderMaterial.material_id == Material.id)
        .group_by(Material.id, Material.name)
        .order_by(func.count(func.distinct(OrderMaterial.order_id)).desc())
        .limit(5)
        .all()
    )

    top_materials = [
        TopMaterial(
            name=m.name,
            total_used_g=round(float(m.total_g), 1),
            order_count=m.order_count,
        )
        for m in top_mats
    ]

    return DashboardStats(
        total_orders=total_orders,
        total_revenue=round(float(total_revenue), 2),
        total_profit=round(float(total_profit), 2),
        avg_profit_margin_percent=avg_margin,
        orders_this_month=month_orders,
        profit_this_month=round(float(month_profit), 2),
        printers=printer_stats,
        maintenance_alerts=maintenance_alerts,
        top_materials=top_materials,
    )
