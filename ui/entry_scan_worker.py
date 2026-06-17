from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

from recognition.entry_recognizer import recognize_entry_plate
from recognition.ocr_reader import stop_ocr_process, warm_up_ocr_reader
from recognition.plate_detector import PlateDetectionError
from services.entry_service import create_vehicle_entry


class EntryScanService(QObject):
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

    @pyqtSlot(object, object, object)
    def scan_entry(self, frame_bgr, user_id: int | None = None, vehicle_type: str = "car") -> None:
        if self._busy:
            return

        self._busy = True
        self.busy_changed.emit(True)
        try:
            frame_bgr = frame_bgr.copy()
            try:
                recognition_result = recognize_entry_plate(frame_bgr)
            except PlateDetectionError as exc:
                self.failed.emit(str(exc))
                return

            entry_result = create_vehicle_entry(
                plate_number=recognition_result["plate_number"],
                frame_bgr=frame_bgr,
                user_id=user_id,
                confidence=recognition_result.get("confidence"),
                vehicle_type=vehicle_type,
            )

            self.finished_ok.emit(entry_result)
        except Exception as exc:
            self.failed.emit(str(exc))
        finally:
            self._busy = False
            self.busy_changed.emit(False)
