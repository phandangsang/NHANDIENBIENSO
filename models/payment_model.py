from database.db import execute, fetch_all, fetch_one


def create_payment(
    parking_record_id: int,
    amount: float,
    duration_minutes: int,
    payment_method: str = "cash",
    status: str = "paid",
    paid_by: int | None = None,
) -> int:
    return execute(
        """
        INSERT INTO `payments`
            (`parking_record_id`, `amount`, `duration_minutes`, `payment_method`, `status`, `paid_by`)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (parking_record_id, amount, duration_minutes, payment_method, status, paid_by),
    )


def find_payment_by_record(parking_record_id: int):
    return fetch_one(
        "SELECT * FROM `payments` WHERE `parking_record_id` = %s",
        (parking_record_id,),
    )


def get_revenue_summary() -> dict:
    row = fetch_one(
        """
        SELECT
            COALESCE(SUM(amount), 0) AS total_revenue,
            COUNT(*) AS total_payments,
            COALESCE(SUM(duration_minutes), 0) AS total_duration_minutes
        FROM payments
        WHERE status = 'paid'
        """
    )
    return row or {}


def list_payment_history(limit: int = 100) -> list[dict]:
    return fetch_all(
        """
        SELECT
            pay.id,
            pay.amount,
            pay.duration_minutes,
            pay.payment_method,
            pay.status,
            pay.paid_at,
            v.plate_number,
            v.vehicle_type,
            pr.entry_time,
            pr.exit_time,
            u.full_name AS paid_by_name
        FROM payments pay
        JOIN parking_records pr ON pr.id = pay.parking_record_id
        JOIN vehicle v ON v.id = pr.vehicle_id
        LEFT JOIN user u ON u.id = pay.paid_by
        ORDER BY pay.paid_at DESC, pay.id DESC
        LIMIT %s
        """,
        (limit,),
    )
