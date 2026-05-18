from models.image_model import create_image
from models.parking_record_model import (
    close_record,
    create_entry_record,
    find_active_record_by_vehicle,
)
from models.vehicle_model import get_or_create_vehicle
from utils.validation import normalize_plate_number


def record_vehicle_entry(
    plate_number: str,
    image_path: str,
    user_id: int | None = None,
    confidence: float | None = None,
) -> int:
    plate_number = normalize_plate_number(plate_number)
    vehicle_id = get_or_create_vehicle(plate_number)
    record_id = create_entry_record(vehicle_id, user_id)

    create_image(record_id, image_path, "entry", plate_number, confidence)
    return record_id


def record_vehicle_exit(
    plate_number: str,
    image_path: str,
    confidence: float | None = None,
) -> int | None:
    plate_number = normalize_plate_number(plate_number)
    vehicle_id = get_or_create_vehicle(plate_number)
    record = find_active_record_by_vehicle(vehicle_id)

    if not record:
        return None

    close_record(record["id"])
    create_image(record["id"], image_path, "exit", plate_number, confidence)
    return record["id"]
