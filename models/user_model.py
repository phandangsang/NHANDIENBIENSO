from database.db import execute, fetch_all, fetch_one


def find_by_username(username: str):
    # Return a dict row (mysql-connector dictionary cursor) for simplicity across UI/services.
    return fetch_one(
        "SELECT * FROM `user` WHERE `username` = %s",
        (username,),
    )


def list_users() -> list[dict]:
    rows = fetch_all(
        """
        SELECT
            u.id,
            u.username,
            u.password,
            u.full_name,
            u.phone,
            u.role,
            u.created_at,
            COUNT(pr.id) AS total_scans
        FROM `user` u
        LEFT JOIN parking_records pr ON pr.user_id = u.id
        GROUP BY u.id, u.username, u.password, u.full_name, u.phone, u.role, u.created_at
        ORDER BY u.id DESC
        """
    )

    users = []
    for row in rows:
        users.append(_present_user(row))
    return users


def create_user(username: str, password: str, full_name: str, role: str, phone: str = "") -> dict:
    user_id = execute(
        """
        INSERT INTO `user` (`username`, `password`, `full_name`, `phone`, `role`)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (username, password, full_name, phone, role),
    )
    return get_user_by_id(user_id)


def update_user(user_id: int, data: dict) -> dict:
    execute(
        """
        UPDATE `user`
        SET `full_name` = %s, `phone` = %s, `role` = %s
        WHERE `id` = %s
        """,
        (data.get("full_name"), data.get("phone"), data.get("role", "staff"), user_id),
    )
    return get_user_by_id(user_id)


def update_password(user_id: int, password: str) -> dict:
    execute(
        "UPDATE `user` SET `password` = %s WHERE `id` = %s",
        (password, user_id),
    )
    return get_user_by_id(user_id)


def delete_user(user_id: int) -> None:
    execute("DELETE FROM `user` WHERE `id` = %s", (user_id,))


def get_user_by_id(user_id: int) -> dict:
    row = fetch_one(
        """
        SELECT
            u.id,
            u.username,
            u.password,
            u.full_name,
            u.phone,
            u.role,
            u.created_at,
            COUNT(pr.id) AS total_scans
        FROM `user` u
        LEFT JOIN parking_records pr ON pr.user_id = u.id
        WHERE u.id = %s
        GROUP BY u.id, u.username, u.password, u.full_name, u.phone, u.role, u.created_at
        """,
        (user_id,),
    )
    return _present_user(row)


def _present_user(row: dict) -> dict:
    if not row:
        return {}

    total_scans = int(row.get("total_scans") or 0)
    user_id = row.get("id")
    return {
        "id": user_id,
        "username": row.get("username"),
        "password": row.get("password"),
        "full_name": row.get("full_name"),
        "phone": row.get("phone"),
        "role": row.get("role") or "staff",
        "created_at": row.get("created_at"),
        "stats": {"total": total_scans},
        "recent_scans": _get_recent_scans(user_id),
    }


def _get_recent_scans(user_id: int | None) -> list[dict]:
    if not user_id:
        return []

    rows = fetch_all(
        """
        SELECT
            pr.id,
            v.plate_number,
            pr.status,
            pr.entry_time,
            pr.exit_time
        FROM parking_records pr
        JOIN vehicle v ON v.id = pr.vehicle_id
        WHERE pr.user_id = %s
        ORDER BY pr.id DESC
        LIMIT 6
        """,
        (user_id,),
    )

    scans = []
    for row in rows:
        status = row.get("status") or "-"
        time_value = row.get("exit_time") if status == "out" else row.get("entry_time")
        scans.append(
            {
                "plate_number": row.get("plate_number"),
                "status": _format_status(status),
                "time": time_value,
            }
        )
    return scans


def _format_status(status: str) -> str:
    status_map = {
        "in": "XE VAO",
        "out": "XE RA",
        "warning": "CANH BAO",
        "deny": "TU CHOI",
    }
    return status_map.get((status or "").lower(), (status or "-").upper())
