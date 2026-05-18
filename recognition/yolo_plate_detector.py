from __future__ import annotations

from dataclasses import dataclass

import cv2


@dataclass(frozen=True)
class PlateDetection:
    x1: int
    y1: int
    x2: int
    y2: int
    confidence: float


def _clamp(value: int, low: int, high: int) -> int:
    return max(low, min(high, value))


def detect_best_plate_bbox(image_bgr, model_path: str):
    """Detect the best (highest confidence) plate bbox using YOLOv8.

    Returns:
        PlateDetection | None
    """
    try:
        from ultralytics import YOLO
    except Exception:
        return None

    model = YOLO(model_path)

    # Ultralytics accepts numpy arrays (BGR ok). Keep it simple.
    results = model.predict(image_bgr, verbose=False)
    if not results:
        return None

    r0 = results[0]
    if r0.boxes is None or len(r0.boxes) == 0:
        return None

    best = None
    for b in r0.boxes:
        conf = float(b.conf.item()) if b.conf is not None else 0.0
        xyxy = b.xyxy[0].tolist()
        x1, y1, x2, y2 = [int(round(v)) for v in xyxy]
        det = PlateDetection(x1=x1, y1=y1, x2=x2, y2=y2, confidence=conf)
        if best is None or det.confidence > best.confidence:
            best = det

    if best is None:
        return None

    h, w = image_bgr.shape[:2]
    x1 = _clamp(best.x1, 0, w - 1)
    y1 = _clamp(best.y1, 0, h - 1)
    x2 = _clamp(best.x2, 0, w)
    y2 = _clamp(best.y2, 0, h)

    if x2 <= x1 or y2 <= y1:
        return None

    return PlateDetection(x1=x1, y1=y1, x2=x2, y2=y2, confidence=best.confidence)


def crop_by_bbox(image_bgr, bbox: PlateDetection):
    return image_bgr[bbox.y1 : bbox.y2, bbox.x1 : bbox.x2].copy()


def draw_bbox(image_bgr, bbox: PlateDetection):
    out = image_bgr.copy()
    cv2.rectangle(out, (bbox.x1, bbox.y1), (bbox.x2, bbox.y2), (0, 255, 0), 2)
    label = f"plate {bbox.confidence:.2f}"
    cv2.putText(out, label, (bbox.x1, max(0, bbox.y1 - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    return out
