from recognition.ocr_reader import read_plate_text
from recognition.plate_detector import detect_plate
from utils.validation import is_valid_plate_number, normalize_plate_number


def recognize_exit_plate(frame_bgr) -> dict:
    import sys

    plate_image, detect_confidence = detect_plate(frame_bgr)
    plate_text, ocr_confidence = read_plate_text(plate_image)
    plate_number = normalize_plate_number(plate_text)

    print(
        f"[DEBUG] EXIT OCR raw='{plate_text}' | normalized='{plate_number}' | "
        f"ocr_conf={ocr_confidence:.2f} | detect_conf={detect_confidence}",
        file=sys.stderr,
    )

    if not is_valid_plate_number(plate_number):
        raise ValueError(
            f"OCR doc duoc: '{plate_text}' -> '{plate_number}' nhung khong dung dinh dang. "
            "Hay dua bien so vao ro hon trong khung hinh."
        )

    return {
        "plate_number": plate_number,
        "confidence": ocr_confidence or detect_confidence,
    }
