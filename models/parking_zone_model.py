from database.db import fetch_all, fetch_one


def list_active_zones(vehicle_type: str | None = None) -> list[dict]:
    sql = """
        SELECT
            z.id,
            z.zone_name,
            z.vehicle_type,
            z.capacity,
            COALESCE(COUNT(pr.id), 0) AS occupied
        FROM parking_zones z
        LEFT JOIN parking_records pr
            ON pr.zone_id = z.id
           AND pr.status = 'in'
           AND pr.exit_time IS NULL
        WHERE z.active = 1
    """
    params = []
    if vehicle_type:
        sql += " AND (z.vehicle_type = %s OR z.vehicle_type = 'all')"
        params.append(vehicle_type)
    sql += """
        GROUP BY z.id, z.zone_name, z.vehicle_type, z.capacity
        ORDER BY z.id ASC
    """
    return fetch_all(sql, tuple(params))


def get_zone_by_id(zone_id: int):
    return fetch_one(
        """
        SELECT
            z.id,
            z.zone_name,
            z.vehicle_type,
            z.capacity,
            COALESCE(COUNT(pr.id), 0) AS occupied
        FROM parking_zones z
        LEFT JOIN parking_records pr
            ON pr.zone_id = z.id
           AND pr.status = 'in'
           AND pr.exit_time IS NULL
        WHERE z.id = %s AND z.active = 1
        GROUP BY z.id, z.zone_name, z.vehicle_type, z.capacity
        """,
        (zone_id,),
    )
