"""
Core price calculation logic for 3D printing cost estimation.

All functions are pure — no database access, no side effects.
This makes them easy to test and reason about.
"""

import re
from dataclasses import dataclass

def parse_time_string(time_str: str, target_unit: str = "hours") -> float:
    """
    Parses a time string like '2d5h43m', '8:30', or '8.5' into float hours or int minutes.
    """
    if not time_str:
        return 0.0
    
    time_str = str(time_str).strip().lower()
    
    # Decimal check (e.g. 8.5 or 8,5)
    if re.match(r'^\d+([.,]\d+)?$', time_str):
        return float(time_str.replace(',', '.'))
    
    # HH:MM check
    match = re.match(r'^(\d+):(\d{1,2})$', time_str)
    if match:
        h = int(match.group(1))
        m = int(match.group(2))
        if target_unit == "hours":
            return h + (m / 60.0)
        else:
            return (h * 60) + m
            
    # Complex format check (d, h, m)
    total_minutes = 0
    found = False
    
    day_match = re.search(r'(\d+)\s*(d|tag)', time_str)
    if day_match:
        total_minutes += int(day_match.group(1)) * 24 * 60
        found = True
        
    hour_match = re.search(r'(\d+)\s*(h|std|stunde)', time_str)
    if hour_match:
        total_minutes += int(hour_match.group(1)) * 60
        found = True
        
    min_match = re.search(r'(\d+)\s*(m|min|minute)', time_str)
    if min_match:
        total_minutes += int(min_match.group(1))
        found = True
        
    if found:
        if target_unit == "hours":
            return total_minutes / 60.0
        else:
            return total_minutes
            
    raise ValueError("Invalid time format")

@dataclass
class CalculationResult:
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


def calculate_price(
    total_material_cost: float,
    print_time_hours: float,
    postprocessing_minutes: int,
    printer_max_wattage: int,
    printer_power_factor: float,
    printer_purchase_price: float,
    printer_expected_lifetime_hours: int,
    electricity_price_per_kwh: float,
    hourly_labor_rate: float,
    maintenance_cost_per_hour: float,
    profit_margin_percent: float,
    labor_factor: float = 1.0,
    other_costs: float = 0.0,
    dryer_max_wattage: int = 0,
    dryer_power_factor: float = 0.0,
    total_dryer_hours: float = 0.0,
    dryer_ams_wattage: int = 0,
    dryer_ams_pf: float = 0.0,
    use_dryer_ams: bool = False,
) -> CalculationResult:
    """
    Calculate the total price for a 3D print job.

    Formula:
        material_cost      = predefined sum of all materials (passed as argument)
        effective_wattage  = max_wattage * power_factor
        electricity_cost   = print_hours * (effective_wattage / 1000) * electricity_price
        depreciation_cost  = print_hours * (purchase_price / lifetime_hours)
        maintenance_cost   = print_hours * maintenance_cost_per_hour
        labor_cost         = (postprocessing_min / 60) * hourly_rate * labor_factor

        subtotal = material + electricity + depreciation + maintenance + labor
        total_price = subtotal * (1 + margin / 100)
        profit = total_price - subtotal
    """
    effective_printer_wattage = printer_max_wattage * printer_power_factor
    # New logic: dryer_max_wattage is the TOTAL maximum. 
    # The heating element power is (Total - AMS).
    # The power factor only applies to the heating element.
    heating_element_max = max(0, dryer_max_wattage - dryer_ams_wattage)
    effective_dryer_wattage = heating_element_max * dryer_power_factor
    effective_ams_wattage = (dryer_ams_wattage * dryer_ams_pf) if use_dryer_ams else 0.0


    
    electricity_cost = (
        (print_time_hours * effective_printer_wattage / 1000) +
        (total_dryer_hours * effective_dryer_wattage / 1000) +
        (print_time_hours * effective_ams_wattage / 1000)
    ) * electricity_price_per_kwh
    depreciation_cost = print_time_hours * (printer_purchase_price / printer_expected_lifetime_hours)
    maintenance_cost = print_time_hours * maintenance_cost_per_hour
    labor_cost = (postprocessing_minutes / 60) * hourly_labor_rate * labor_factor

    subtotal = total_material_cost + electricity_cost + depreciation_cost + maintenance_cost + labor_cost + other_costs
    total_price = subtotal * (1 + profit_margin_percent / 100)
    profit = total_price - subtotal

    return CalculationResult(
        material_cost=round(total_material_cost, 2),
        electricity_cost=round(electricity_cost, 2),
        depreciation_cost=round(depreciation_cost, 2),
        maintenance_cost=round(maintenance_cost, 2),
        labor_cost=round(labor_cost, 2),
        other_costs=round(other_costs, 2),
        subtotal=round(subtotal, 2),
        profit_margin_percent=profit_margin_percent,
        profit=round(profit, 2),
        total_price=round(total_price, 2),
    )
