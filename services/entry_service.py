from datetime import datetime

import cv2

from config import ENTRY_IMAGE_DIR
from models.parking_record_model import find_active_record_by_vehicle
from models.vehicle_model import find_by_plate_number
from services.parking_service import record_vehicle_entry


def create_vehicle_entry(
    plate_number: str,
    frame_bgr,
    user_id: int | None,
    confidence=None,
    vehicle_type: str = "car",
) -> dict:
    vehicle = find_by_plate_number(plate_number)
    if vehicle:
        active_record = find_active_record_by_vehicle(int(vehicle["id"]))
        if active_record:
            raise ValueError(f"Xe {plate_number} dang o trong bai.")

    image_path = save_entry_image(frame_bgr, plate_number)
    record_id = record_vehicle_entry(
        plate_number=plate_number,
        image_path=image_path,
        user_id=user_id,
        confidence=confidence,
        vehicle_type=vehicle_type,
    )

    return {
        "record_id": record_id,
        "plate_number": plate_number,
        "vehicle_type": vehicle_type,
        "image_path": image_path,
        "confidence": confidence,
        "captured_at": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
    }


def save_entry_image(frame_bgr, plate_number: str) -> str:
    ENTRY_IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    image_path = ENTRY_IMAGE_DIR / f"{plate_number}_{timestamp}.jpg"
    cv2.imwrite(str(image_path), frame_bgr)
    return str(image_path)
