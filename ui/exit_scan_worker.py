from PyQt5.QtCore import QThread, pyqtSignal

from recognition.exit_recognizer import recognize_exit_plate
from recognition.plate_detector import PlateDetectionError
from services.exit_service import find_active_entry_record


class ExitScanWorker(QThread):
    found = pyqtSignal(dict)
    not_found = pyqtSignal(str, str)
    failed = pyqtSignal(str)

    def __init__(self, frame_bgr):
        super().__init__()
        self.frame_bgr = frame_bgr.copy()

    def run(self) -> None:
        try:
            try:
                result = recognize_exit_plate(self.frame_bgr)
            except PlateDetectionError as exc:
                self.failed.emit(str(exc))
                return

            plate_number = result["plate_number"]
            entry_record = find_active_entry_record(plate_number)
            if not entry_record:
                self.not_found.emit(f"Khong tim thay xe {plate_number} dang trong bai.", plate_number)
                return

            self.found.emit(
                {
                    "plate_number": plate_number,
                    "confidence": result.get("confidence"),
                    "entry_record": entry_record,
                }
            )
        except Exception as exc:
            self.failed.emit(str(exc))
