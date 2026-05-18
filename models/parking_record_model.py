def create_entry_record(vehicle_id: int, user_id: int | None = None) -> int:
    from database.db import execute

    return execute(
        "INSERT INTO `parking_records` (`vehicle_id`, `user_id`, `status`) VALUES (%s, %s, 'in')",
        (vehicle_id, user_id),
    )


def find_active_record_by_vehicle(vehicle_id: int):
    from database.db import fetch_one

    return fetch_one(
        """
        SELECT *
        FROM `parking_records`
        WHERE `vehicle_id` = %s AND `status` = 'in'
        ORDER BY `entry_time` DESC
        LIMIT 1
        """,
        (vehicle_id,),
    )


def close_record(record_id: int) -> None:
    from database.db import execute

    execute(
        """
        UPDATE `parking_records`
        SET `exit_time` = CURRENT_TIMESTAMP, `status` = 'out'
        WHERE `id` = %s
        """,
        (record_id,),
    )


def list_history():
    from database.db import fetch_all

    return fetch_all(
        """
        SELECT
            pr.*,
            v.`plate_number`,
            v.`vehicle_type`
        FROM `parking_records` pr
        JOIN `vehicle` v ON v.`id` = pr.`vehicle_id`
        ORDER BY pr.`entry_time` DESC
        """
    )
