import os
from datetime import datetime

import cv2
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from config import BASE_DIR
from database.db import fetch_one
from models.image_model import create_image
from models.parking_record_model import close_record

EXIT_IMAGE_DIR = BASE_DIR / "storage" / "exit_images"


def _load_exit_style():
    style_path = os.path.join(os.path.dirname(__file__), "style", "exit.css")
    try:
        with open(style_path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        return ""


class ExitWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ExitWindow")
        self.setStyleSheet(_load_exit_style())

        self.exit_entry_record = None
        self.exit_capture_path = None
        self.current_frame = None

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

        plate_row = QHBoxLayout()
        self.exit_plate_input = QLineEdit()
        self.exit_plate_input.setPlaceholderText("Nhap bien so quet duoc, vi du: 51G-999.00")
        self.exit_plate_input.setFixedHeight(42)

        self.compare_exit_btn = QPushButton("DOI CHIEU")
        self.compare_exit_btn.setObjectName("PrimaryButton")
        self.compare_exit_btn.setFixedHeight(42)
        self.compare_exit_btn.clicked.connect(self.compare_exit_plate)

        plate_row.addWidget(self.exit_plate_input, 4)
        plate_row.addWidget(self.compare_exit_btn, 1)
        main_layout.addLayout(plate_row)

        self.exit_info_frame = QFrame()
        self.exit_info_frame.setObjectName("info_frame")
        info_layout = QGridLayout(self.exit_info_frame)

        self.exit_plate_label = QLabel("--")
        self.exit_plate_label.setAlignment(Qt.AlignCenter)
        self.exit_plate_label.setObjectName("plate_label")

        self.exit_status_label = QLabel("Cho quet xe ra")
        self.exit_status_label.setAlignment(Qt.AlignCenter)
        self.exit_status_label.setObjectName("time_label")

        info_layout.addWidget(self.exit_plate_label, 0, 0)
        info_layout.addWidget(self.exit_status_label, 0, 1)
        main_layout.addWidget(self.exit_info_frame)

        self.confirm_exit_btn = QPushButton("XAC NHAN XE RA")
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

    def capture_exit_image(self):
        if self.current_frame is None:
            QMessageBox.warning(self, "Camera", "Chua co hinh anh tu camera quet xe ra.")
            return None

        EXIT_IMAGE_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        plate = self.exit_plate_label.text() or "unknown"
        filepath = EXIT_IMAGE_DIR / f"{plate}_{timestamp}.jpg"
        cv2.imwrite(str(filepath), self.current_frame)
        self.exit_capture_path = str(filepath)
        return str(filepath)

    def compare_exit_plate(self) -> None:
        plate_number = self.exit_plate_input.text().strip().upper()
        if not plate_number:
            QMessageBox.warning(self, "Thieu bien so", "Vui long nhap bien so xe ra de doi chieu.")
            return

        self.exit_entry_record = self._find_active_entry_record(plate_number)
        self.exit_plate_label.setText(plate_number)

        if not self.exit_entry_record:
            self.entry_image_label.setText("Khong tim thay xe dang trong bai")
            self.entry_image_label.setPixmap(QPixmap())
            self.exit_status_label.setText("KHONG THONG QUA")
            self.confirm_exit_btn.setEnabled(False)
            return

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
        self.exit_status_label.setText(f"THONG QUA - Vao luc: {entry_time}")
        self.confirm_exit_btn.setEnabled(True)

    def confirm_exit_vehicle(self) -> None:
        if not self.exit_entry_record:
            QMessageBox.warning(self, "Chua doi chieu", "Vui long doi chieu bien so truoc khi xac nhan.")
            return

        exit_image_path = self.capture_exit_image()
        if not exit_image_path:
            return

        record_id = self.exit_entry_record.get("parking_record_id")
        plate_number = self.exit_plate_label.text()

        close_record(record_id)
        create_image(record_id, exit_image_path, "exit", plate_number)

        self.exit_status_label.setText("DA XAC NHAN XE RA")
        self.confirm_exit_btn.setEnabled(False)
        self.exit_entry_record = None
        QMessageBox.information(self, "Thanh cong", "Da xac nhan xe ra va luu vao he thong.")

    def _find_active_entry_record(self, plate_number: str):
        return fetch_one(
            """
            SELECT
                pr.id AS parking_record_id,
                pr.entry_time,
                v.id AS vehicle_id,
                v.plate_number,
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
