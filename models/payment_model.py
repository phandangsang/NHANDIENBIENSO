from database.db import execute, fetch_one


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
