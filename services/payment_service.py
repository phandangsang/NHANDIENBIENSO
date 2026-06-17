from __future__ import annotations

import math
from datetime import datetime
from decimal import Decimal

from database.db import fetch_one
from models.payment_model import create_payment


def calculate_parking_fee(entry_record: dict, exit_time: datetime | None = None) -> dict:
    exit_time = exit_time or datetime.now()
    entry_time = _as_datetime(entry_record.get("entry_time"))
    vehicle_type = entry_record.get("vehicle_type") or "car"

    duration_minutes = max(1, math.ceil((exit_time - entry_time).total_seconds() / 60))
    rule = _get_active_fee_rule(vehicle_type) or _get_active_fee_rule("car") or _default_rule()

    first_minutes = int(rule.get("first_block_minutes") or 60)
    first_price = _to_float(rule.get("first_block_price"))
    next_hour_price = _to_float(rule.get("next_hour_price"))
    daily_max_price = rule.get("daily_max_price")

    if duration_minutes <= first_minutes:
        amount = first_price
    else:
        extra_minutes = duration_minutes - first_minutes
        extra_hours = math.ceil(extra_minutes / 60)
        amount = first_price + extra_hours * next_hour_price

    if daily_max_price is not None:
        amount = min(amount, _to_float(daily_max_price))

    return {
        "amount": float(amount),
        "duration_minutes": duration_minutes,
        "vehicle_type": vehicle_type,
        "rule": rule,
        "entry_time": entry_time,
        "exit_time": exit_time,
    }


def create_exit_payment(
    entry_record: dict,
    paid_by: int | None = None,
    payment_method: str = "cash",
) -> dict:
    fee = calculate_parking_fee(entry_record)
    payment_id = create_payment(
        parking_record_id=int(entry_record.get("parking_record_id")),
        amount=fee["amount"],
        duration_minutes=fee["duration_minutes"],
        payment_method=payment_method,
        status="paid",
        paid_by=paid_by,
    )
    fee["payment_id"] = payment_id
    fee["payment_method"] = payment_method
    return fee


def format_money(amount: float) -> str:
    return f"{amount:,.0f} VND".replace(",", ".")


def format_duration(minutes: int) -> str:
    hours = minutes // 60
    mins = minutes % 60
    if hours and mins:
        return f"{hours} gio {mins} phut"
    if hours:
        return f"{hours} gio"
    return f"{mins} phut"


def _get_active_fee_rule(vehicle_type: str):
    return fetch_one(
        """
        SELECT *
        FROM `fee_rules`
        WHERE `vehicle_type` = %s AND `active` = 1
        ORDER BY `id` DESC
        LIMIT 1
        """,
        (vehicle_type,),
    )


def _as_datetime(value) -> datetime:
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        return datetime.fromisoformat(value)
    raise ValueError("Thoi gian xe vao khong hop le.")


def _to_float(value) -> float:
    if isinstance(value, Decimal):
        return float(value)
    return float(value or 0)


def _default_rule() -> dict:
    return {
        "vehicle_type": "car",
        "first_block_minutes": 60,
        "first_block_price": 20000,
        "next_hour_price": 10000,
        "daily_max_price": 150000,
    }
