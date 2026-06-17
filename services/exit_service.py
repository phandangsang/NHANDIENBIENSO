from datetime import datetime

import cv2

from config import BASE_DIR
from database.db import fetch_one
from models.image_model import create_image
from models.parking_record_model import close_record
from services.payment_service import create_exit_payment


EXIT_IMAGE_DIR = BASE_DIR / "storage" / "exit_images"


def find_active_entry_record(plate_number: str):
    return fetch_one(
        """
        SELECT
            pr.id AS parking_record_id,
            pr.entry_time,
            v.id AS vehicle_id,
            v.plate_number,
            v.vehicle_type,
            img.image_path
        FROM parking_records pr
        JOIN vehicle v ON v.id = pr.vehicle_id
        LEFT JOIN images img
            ON img.parking_record_id = pr.id
           AND img.image_type = 'entry'
        WHERE v.plate_number = %s
          AND pr.exit_time IS NULL
          AND pr.status = 'in'
        ORDER BY pr.entry_time DESC, img.captured_at DESC
        LIMIT 1
        """,
        (plate_number,),
    )


def confirm_vehicle_exit(
    entry_record: dict,
    plate_number: str,
    frame_bgr,
    confidence=None,
    paid_by: int | None = None,
) -> dict:
    record_id = entry_record.get("parking_record_id")
    image_path = save_exit_image(frame_bgr, plate_number)

    close_record(record_id)
    create_image(record_id, image_path, "exit", plate_number, confidence)
    payment = create_exit_payment(entry_record, paid_by=paid_by)

    return {
        "image_path": image_path,
        "payment": payment,
    }


def save_exit_image(frame_bgr, plate_number: str) -> str:
    EXIT_IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    image_path = EXIT_IMAGE_DIR / f"{plate_number}_{timestamp}.jpg"
    cv2.imwrite(str(image_path), frame_bgr)
    return str(image_path)
