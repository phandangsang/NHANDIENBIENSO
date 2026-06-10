from __future__ import annotations

from datetime import datetime

import cv2
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

from config import ENTRY_IMAGE_DIR
from models.parking_record_model import find_active_record_by_vehicle
from models.vehicle_model import find_by_plate_number
from recognition.ocr_reader import read_plate_text, stop_ocr_process, warm_up_ocr_reader
from recognition.plate_detector import PlateDetectionError, detect_plate
from services.parking_service import record_vehicle_entry
from utils.validation import is_valid_plate_number, normalize_plate_number


class EntryRecognitionService(QObject):
    ready = pyqtSignal()
    finished_ok = pyqtSignal(dict)
    failed = pyqtSignal(str)
    preload_failed = pyqtSignal(str)
    busy_changed = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self._busy = False

    @pyqtSlot()
    def preload(self) -> None:
        try:
            warm_up_ocr_reader()
            self.ready.emit()
        except Exception as exc:
            self.preload_failed.emit(str(exc))

    @pyqtSlot()
    def shutdown(self) -> None:
        stop_ocr_process()

    @pyqtSlot(object, object)
    def scan_entry(self, frame_bgr, user_id: int | None = None) -> None:
        if self._busy:
            return

        self._busy = True
        self.busy_changed.emit(True)
        try:
            frame_bgr = frame_bgr.copy()
            try:
                plate_image, detect_confidence = detect_plate(frame_bgr)
            except PlateDetectionError as exc:
                self.failed.emit(str(exc))
                return

            plate_text, ocr_confidence = read_plate_text(plate_image)
            plate_number = normalize_plate_number(plate_text)

            if not is_valid_plate_number(plate_number):
                self.failed.emit(
                    "Ket qua OCR khong dung dinh dang bien so Viet Nam. "
                    "Hay dua bien so vao ro hon trong khung hinh."
                )
                return

            vehicle = find_by_plate_number(plate_number)
            if vehicle:
                active_record = find_active_record_by_vehicle(int(vehicle["id"]))
                if active_record:
                    self.failed.emit(f"Xe {plate_number} dang o trong bai.")
                    return

            image_path = self._save_entry_image(plate_number, frame_bgr)
            confidence = ocr_confidence or detect_confidence
            record_id = record_vehicle_entry(
                plate_number=plate_number,
                image_path=image_path,
                user_id=user_id,
                confidence=confidence,
            )

            self.finished_ok.emit(
                {
                    "record_id": record_id,
                    "plate_number": plate_number,
                    "image_path": image_path,
                    "confidence": confidence,
                    "captured_at": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                }
            )
        except Exception as exc:
            self.failed.emit(str(exc))
        finally:
            self._busy = False
            self.busy_changed.emit(False)

    def _save_entry_image(self, plate_number: str, frame_bgr) -> str:
        ENTRY_IMAGE_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_path = ENTRY_IMAGE_DIR / f"{plate_number}_{timestamp}.jpg"
        cv2.imwrite(str(image_path), frame_bgr)
        return str(image_path)
