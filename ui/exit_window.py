import os
from datetime import datetime

import cv2
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from services.exit_service import confirm_vehicle_exit
from services.payment_service import calculate_parking_fee, format_duration, format_money
from .exit_scan_worker import ExitScanWorker


def _load_exit_style():
    style_path = os.path.join(os.path.dirname(__file__), "style", "exit.css")
    try:
        with open(style_path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        return ""


class ExitWindow(QWidget):
    vehicle_exited = pyqtSignal()

    def __init__(self, user: dict | None = None, parent=None):
        super().__init__(parent)
        self.user = user or {}
        self.setObjectName("ExitWindow")
        self.setStyleSheet(_load_exit_style())

        self.exit_entry_record = None
        self.exit_capture_path = None
        self.current_frame = None
        self.exit_confidence = None
        self.exit_scan_worker = None
        self.exit_fee = None

        self._build_ui()

    def _build_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        title = QLabel("QUET BIEN SO XE RA")
        title.setObjectName("PageTitle")
        main_layout.addWidget(title)

        compare_row = QHBoxLayout()
        compare_row.setSpacing(18)

        exit_camera_frame = QFrame()
        exit_camera_frame.setObjectName("CompareCard")
        exit_camera_layout = QVBoxLayout(exit_camera_frame)
        exit_camera_layout.setContentsMargins(16, 16, 16, 16)
        exit_camera_layout.setSpacing(12)

        camera_title = QLabel("Camera xe ra")
        camera_title.setObjectName("SectionTitle")
        self.exit_camera_label = QLabel("Dang cho camera...")
        self.exit_camera_label.setObjectName("ExitCameraPreview")
        self.exit_camera_label.setFixedHeight(360)
        self.exit_camera_label.setAlignment(Qt.AlignCenter)

        exit_camera_layout.addWidget(camera_title)
        exit_camera_layout.addWidget(self.exit_camera_label)

        entry_image_frame = QFrame()
        entry_image_frame.setObjectName("CompareCard")
        entry_image_layout = QVBoxLayout(entry_image_frame)
        entry_image_layout.setContentsMargins(16, 16, 16, 16)
        entry_image_layout.setSpacing(12)

        entry_title = QLabel("Anh xe luc vao")
        entry_title.setObjectName("SectionTitle")
        self.entry_image_label = QLabel("Nhap bien so de lay anh xe vao")
        self.entry_image_label.setObjectName("EntryImagePreview")
        self.entry_image_label.setFixedHeight(360)
        self.entry_image_label.setAlignment(Qt.AlignCenter)

        entry_image_layout.addWidget(entry_title)
        entry_image_layout.addWidget(self.entry_image_label)

        compare_row.addWidget(exit_camera_frame)
        compare_row.addWidget(entry_image_frame)
        main_layout.addLayout(compare_row)

        self.scan_exit_btn = QPushButton("QUET TU CAMERA")
        self.scan_exit_btn.setObjectName("PrimaryButton")
        self.scan_exit_btn.setFixedHeight(50)
        self.scan_exit_btn.clicked.connect(self.scan_exit_plate)

        main_layout.addWidget(self.scan_exit_btn)

        self.exit_info_frame = QFrame()
        self.exit_info_frame.setObjectName("info_frame")
        info_layout = QGridLayout(self.exit_info_frame)

        self.exit_plate_label = QLabel("--")
        self.exit_plate_label.setAlignment(Qt.AlignCenter)
        self.exit_plate_label.setObjectName("plate_label")

        self.exit_status_label = QLabel("Cho quet xe ra")
        self.exit_status_label.setAlignment(Qt.AlignCenter)
        self.exit_status_label.setObjectName("time_label")

        self.exit_fee_label = QLabel("Phi gui xe: --")
        self.exit_fee_label.setAlignment(Qt.AlignCenter)
        self.exit_fee_label.setObjectName("time_label")

        info_layout.addWidget(self.exit_plate_label, 0, 0)
        info_layout.addWidget(self.exit_status_label, 0, 1)
        info_layout.addWidget(self.exit_fee_label, 1, 0, 1, 2)
        main_layout.addWidget(self.exit_info_frame)

        self.confirm_exit_btn = QPushButton("XAC NHAN THU PHI VA XE RA")
        self.confirm_exit_btn.setObjectName("ConfirmButton")
        self.confirm_exit_btn.setFixedHeight(50)
        self.confirm_exit_btn.clicked.connect(self.confirm_exit_vehicle)
        self.confirm_exit_btn.setEnabled(False)
        main_layout.addWidget(self.confirm_exit_btn)
        main_layout.addStretch()

    def update_camera_frame(self, frame) -> None:
        self.current_frame = frame.copy()
        self._show_frame(frame, self.exit_camera_label)
        if self.exit_entry_record is None:
            self.exit_status_label.setText(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

    def scan_exit_plate(self) -> None:
        if self.current_frame is None:
            QMessageBox.warning(self, "Camera", "Chua co hinh anh tu camera quet xe ra.")
            return

        if self.exit_scan_worker is not None and self.exit_scan_worker.isRunning():
            return

        self.scan_exit_btn.setEnabled(False)
        self.confirm_exit_btn.setEnabled(False)
        self.exit_status_label.setText("DANG QUET BIEN SO XE RA...")
        self.exit_plate_label.setText("--")
        self.exit_fee_label.setText("Phi gui xe: --")
        self.exit_fee = None
        self.entry_image_label.setPixmap(QPixmap())
        self.entry_image_label.setText("Dang tim anh xe luc vao...")

        self.exit_scan_worker = ExitScanWorker(self.current_frame)
        self.exit_scan_worker.found.connect(self._on_exit_scan_found)
        self.exit_scan_worker.not_found.connect(self._on_exit_scan_not_found)
        self.exit_scan_worker.failed.connect(self._on_exit_scan_failed)
        self.exit_scan_worker.finished.connect(self._on_exit_scan_finished)
        self.exit_scan_worker.start()

    def _on_exit_scan_found(self, data: dict) -> None:
        plate_number = data["plate_number"]
        self.exit_confidence = data.get("confidence")
        self.exit_entry_record = data.get("entry_record")
        self._show_entry_record(plate_number, self.exit_entry_record)

    def _on_exit_scan_not_found(self, message: str, plate_number: str) -> None:
        if plate_number:
            self.exit_plate_label.setText(plate_number)
        self.entry_image_label.setText("Khong tim thay xe dang trong bai")
        self.entry_image_label.setPixmap(QPixmap())
        self.exit_status_label.setText("KHONG THONG QUA")
        self.exit_fee_label.setText("Phi gui xe: --")
        self.confirm_exit_btn.setEnabled(False)
        QMessageBox.warning(self, "Xe ra", message)

    def _on_exit_scan_failed(self, message: str) -> None:
        self.entry_image_label.setText("Khong the quet bien so xe ra")
        self.entry_image_label.setPixmap(QPixmap())
        self.exit_status_label.setText("QUET THAT BAI")
        self.exit_fee_label.setText("Phi gui xe: --")
        self.confirm_exit_btn.setEnabled(False)
        QMessageBox.warning(self, "Nhan dien that bai", message)

    def _on_exit_scan_finished(self) -> None:
        self.scan_exit_btn.setEnabled(True)

    def _show_entry_record(self, plate_number: str, entry_record) -> None:
        self.exit_plate_label.setText(plate_number)

        if not entry_record:
            self.entry_image_label.setText("Khong tim thay xe dang trong bai")
            self.entry_image_label.setPixmap(QPixmap())
            self.exit_status_label.setText("KHONG THONG QUA")
            self.confirm_exit_btn.setEnabled(False)
            return

        self.exit_entry_record = entry_record
        image_path = self.exit_entry_record.get("image_path")
        if image_path and os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            self.entry_image_label.setPixmap(
                pixmap.scaled(
                    self.entry_image_label.width(),
                    self.entry_image_label.height(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation,
                )
            )
        else:
            self.entry_image_label.setPixmap(QPixmap())
            self.entry_image_label.setText("Co ban ghi xe vao nhung chua co anh")

        entry_time = self.exit_entry_record.get("entry_time")
        status = f"THONG QUA - Vao luc: {entry_time}"
        if self.exit_confidence is not None:
            status += f" - OCR: {float(self.exit_confidence) * 100:.1f}%"
        self.exit_status_label.setText(status)
        self.exit_fee = calculate_parking_fee(self.exit_entry_record)
        self.exit_fee_label.setText(
            f"Thoi gian gui: {format_duration(self.exit_fee['duration_minutes'])} - "
            f"Phi: {format_money(self.exit_fee['amount'])}"
        )
        self.confirm_exit_btn.setEnabled(True)

    def confirm_exit_vehicle(self) -> None:
        if not self.exit_entry_record:
            QMessageBox.warning(self, "Chua doi chieu", "Vui long doi chieu bien so truoc khi xac nhan.")
            return

        if self.current_frame is None:
            QMessageBox.warning(self, "Camera", "Chua co hinh anh tu camera quet xe ra.")
            return

        plate_number = self.exit_plate_label.text()
        result = confirm_vehicle_exit(
            self.exit_entry_record,
            plate_number,
            self.current_frame,
            self.exit_confidence,
            paid_by=self.user.get("id"),
        )
        self.exit_capture_path = result.get("image_path")
        payment = result.get("payment") or {}

        self.exit_status_label.setText("DA XAC NHAN THU PHI VA XE RA")
        self.exit_fee_label.setText(
            f"Da thu: {format_money(payment.get('amount', 0))} - "
            f"{format_duration(int(payment.get('duration_minutes', 0)))}"
        )
        self.confirm_exit_btn.setEnabled(False)
        self.exit_entry_record = None
        self.exit_confidence = None
        self.exit_fee = None
        self.vehicle_exited.emit()
        QMessageBox.information(
            self,
            "Thanh cong",
            f"Da xac nhan xe ra va thu phi {format_money(payment.get('amount', 0))}.",
        )

    def _show_frame(self, frame, label: QLabel) -> None:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        img = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
        pix = QPixmap.fromImage(img)
        label.setPixmap(
            pix.scaled(
                label.width(),
                label.height(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
        )
