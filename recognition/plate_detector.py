from config import YOLO_MODEL_PATH, YOLO_USE
from recognition.yolo_plate_detector import crop_by_bbox, detect_best_plate_bbox


def detect_plate(image_bgr):
    """Tra ve anh vung bien so (crop).

    - Neu `YOLO_USE = True` va co model, dung YOLOv8 de detect bbox roi cat.
    - Neu khong, fallback: tra ve anh goc (de OCR tu xu ly hoac dung OpenCV sau).

    Returns:
        (plate_image_bgr, confidence)
    """
    if not YOLO_USE or not YOLO_MODEL_PATH:
        return image_bgr, None

    try:
        bbox = detect_best_plate_bbox(image_bgr, str(YOLO_MODEL_PATH))
    except Exception:
        bbox = None

    if not bbox:
        return image_bgr, None

    return crop_by_bbox(image_bgr, bbox), bbox.confidence
