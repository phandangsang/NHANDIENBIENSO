from models.parking_zone_model import get_zone_by_id, list_active_zones


def get_available_zones(vehicle_type: str | None = None) -> list[dict]:
    zones = []
    for zone in list_active_zones(vehicle_type):
        capacity = int(zone.get("capacity") or 0)
        occupied = int(zone.get("occupied") or 0)
        zone["available"] = max(0, capacity - occupied)
        zones.append(zone)
    return zones


def ensure_zone_available(zone_id: int | None, vehicle_type: str) -> dict | None:
    if not zone_id:
        return None

    zone = get_zone_by_id(zone_id)
    if not zone:
        raise ValueError("Khu vuc khong ton tai hoac da bi tat.")

    zone_vehicle_type = zone.get("vehicle_type") or "all"
    if zone_vehicle_type not in ("all", vehicle_type):
        raise ValueError("Khu vuc nay khong phu hop voi loai xe da chon.")

    capacity = int(zone.get("capacity") or 0)
    occupied = int(zone.get("occupied") or 0)
    available = max(0, capacity - occupied)
    if available <= 0:
        raise ValueError(f"{zone.get('zone_name')} da het cho trong.")

    zone["available"] = available
    return zone
