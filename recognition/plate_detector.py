from datetime import datetime

import cv2

from config import BASE_DIR, YOLO_MODEL_PATH, YOLO_USE
from recognition.yolo_plate_detector import (
    crop_by_bbox,
    detect_best_plate_bbox,
    detect_best_plate_bbox_from_path,
)


class PlateDetectionError(Exception):
    pass


def detect_plate(image_bgr):
    """Tra ve anh vung bien so (crop).

    - Neu `YOLO_USE = True` va co model, dung YOLOv8 de detect bbox roi cat.
    - Neu YOLO dang bat nhung khong thay bien so, dung lai de tranh OCR toan anh.
    - Neu YOLO_USE = False, fallback: tra ve anh goc.

    Returns:
        (plate_image_bgr, confidence)
    """
    if not YOLO_USE or not YOLO_MODEL_PATH:
        return image_bgr, None

    try:
        bbox = detect_best_plate_bbox(image_bgr, str(YOLO_MODEL_PATH))
    except Exception as exc:
        debug_path = _save_debug_frame(image_bgr)
        raise PlateDetectionError(
            "YOLO bi loi khi detect bien so. "
            f"Loi: {exc}. Anh debug: {debug_path}"
        ) from exc

    if not bbox:
        debug_path = _save_debug_frame(image_bgr)
        bbox = detect_best_plate_bbox_from_path(debug_path, str(YOLO_MODEL_PATH))
        if bbox:
            return crop_by_bbox(image_bgr, bbox), bbox.confidence

        # Fallback: YOLO khong detect duoc -> tra ve anh goc de OCR xu ly
        import sys
        print(
            f"[WARN] YOLO khong tim thay bien so, fallback OCR toan anh. "
            f"Debug: {debug_path}",
            file=sys.stderr,
        )
        return image_bgr, None

    return crop_by_bbox(image_bgr, bbox), bbox.confidence


def _save_debug_frame(image_bgr) -> str:
    debug_dir = BASE_DIR / "storage" / "debug"
    debug_dir.mkdir(parents=True, exist_ok=True)
    filename = datetime.now().strftime("yolo_failed_%Y%m%d_%H%M%S.jpg")
    debug_path = debug_dir / filename
    cv2.imwrite(str(debug_path), image_bgr)
    return str(debug_path)
