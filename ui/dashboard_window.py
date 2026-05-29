import os
from datetime import datetime

import cv2
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import (
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from .sidebar import Sidebar
from .user_window import UserPage
from .vehicles_window import VehiclesWindow


class DashboardWindow(QMainWindow):
    logout_requested = pyqtSignal()

    def __init__(self, user: dict):
        super().__init__()
        self.user = user

        self.setWindowTitle("LPR Dashboard")
        self.resize(1200, 700)

        self.cap1 = None
        self.cap2 = None
        self.frame_cam2 = None

        self.cap1_index = 0
        self.cap2_index = 1

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_camera)

        self._build_ui()
        self._load_styles()
        self._open_cameras()
        self.timer.start(30)

    def closeEvent(self, event):
        self.timer.stop()
        self._release_cameras()
        event.accept()

    def _load_styles(self) -> None:
        base_path = os.path.dirname(os.path.abspath(__file__))
        qss_path = os.path.join(base_path, "style", "dashboard.qss")
        try:
            with open(qss_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            pass

    def _build_ui(self) -> None:
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.sidebar = Sidebar()
        self.stack = QStackedWidget()

        self.page_dashboard = self._create_dashboard_page()
        self.page_vehicles = VehiclesWindow()
        self.page_users = UserPage()
        self.page_history = self._create_simple_page("HISTORY")
        self.page_settings = self._create_simple_page("SETTINGS")

        # Keep indexes aligned with ui/sidebar.py (0..4)
        self.stack.addWidget(self.page_dashboard)  # 0
        self.stack.addWidget(self.page_vehicles)   # 1
        self.stack.addWidget(self.page_users)      # 2
        self.stack.addWidget(self.page_history)    # 3
        self.stack.addWidget(self.page_settings)   # 4

        self.sidebar.pageChanged.connect(self.change_page)

        main_layout.addWidget(self.sidebar, 1)
        main_layout.addWidget(self.stack, 5)

    def _create_dashboard_page(self) -> QWidget:
        page = QWidget()
        main_layout = QVBoxLayout(page)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        camera_row = QHBoxLayout()

        cam1 = self._create_camera_block("Camera nhan dien", 0)
        cam2 = self._create_camera_block("Camera chup anh", 1)

        self.camera_label_1 = cam1["label"]
        self.camera_label_2 = cam2["label"]
        self.cam1_select = cam1["combo"]
        self.cam2_select = cam2["combo"]

        self.cam1_select.currentIndexChanged.connect(self.change_camera_1)
        self.cam2_select.currentIndexChanged.connect(self.change_camera_2)

        camera_row.addWidget(cam1["frame"])
        camera_row.addWidget(cam2["frame"])

        self.info_frame = QFrame()
        self.info_frame.setObjectName("info_frame")
        info_layout = QGridLayout(self.info_frame)

        self.plate_label = QLabel("--")
        self.plate_label.setAlignment(Qt.AlignCenter)
        self.plate_label.setObjectName("plate_label")

        self.time_label = QLabel("--")
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setObjectName("time_label")

        info_layout.addWidget(self.plate_label, 0, 0)
        info_layout.addWidget(self.time_label, 0, 1)

        self.confirm_btn = QPushButton("XAC NHAN")
        self.confirm_btn.setFixedHeight(50)
        self.confirm_btn.clicked.connect(self.capture_image)

        main_layout.addLayout(camera_row)
        main_layout.addWidget(self.info_frame)
        main_layout.addWidget(self.confirm_btn)
        main_layout.addStretch()

        return page

    def _create_camera_block(self, title_text: str, default_index: int) -> dict:
        frame = QFrame()
        layout = QVBoxLayout(frame)

        top = QHBoxLayout()
        title = QLabel(title_text)

        combo = QComboBox()
        combo.addItems(["Camera 0", "Camera 1", "Camera 2", "Camera 3"])
        combo.setCurrentIndex(default_index)

        top.addWidget(title)
        top.addStretch()
        top.addWidget(combo)

        cam_label = QLabel()
        cam_label.setFixedSize(500, 300)
        cam_label.setAlignment(Qt.AlignCenter)

        layout.addLayout(top)
        layout.addWidget(cam_label)

        return {"frame": frame, "label": cam_label, "combo": combo}

    def _create_simple_page(self, name: str) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)

        label = QLabel(name)
        label.setStyleSheet("font-size:24px;font-weight:bold;")
        layout.addWidget(label)
        layout.addStretch()

        return page

    def _open_cameras(self) -> None:
        self._release_cameras()
        self.cap1 = cv2.VideoCapture(self.cap1_index, cv2.CAP_DSHOW)
        self.cap2 = cv2.VideoCapture(self.cap2_index, cv2.CAP_DSHOW)

    def _release_cameras(self) -> None:
        if self.cap1 is not None:
            try:
                self.cap1.release()
            except Exception:
                pass
        if self.cap2 is not None:
            try:
                self.cap2.release()
            except Exception:
                pass
        self.cap1 = None
        self.cap2 = None

    def update_camera(self) -> None:
        if self.cap1 is not None and self.cap1.isOpened():
            ret1, frame1 = self.cap1.read()
            if ret1 and frame1 is not None:
                self.show_frame(frame1, self.camera_label_1)

        if self.cap2 is not None and self.cap2.isOpened():
            ret2, frame2 = self.cap2.read()
            if ret2 and frame2 is not None:
                self.frame_cam2 = frame2.copy()
                self.show_frame(frame2, self.camera_label_2)

        self.time_label.setText(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

    def show_frame(self, frame, label: QLabel) -> None:
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

    def change_camera_1(self, index: int) -> None:
        self.cap1_index = index
        if self.cap1 is not None:
            try:
                self.cap1.release()
            except Exception:
                pass
        self.cap1 = cv2.VideoCapture(index, cv2.CAP_DSHOW)

    def change_camera_2(self, index: int) -> None:
        self.cap2_index = index
        if self.cap2 is not None:
            try:
                self.cap2.release()
            except Exception:
                pass
        self.cap2 = cv2.VideoCapture(index, cv2.CAP_DSHOW)

    def capture_image(self) -> None:
        if self.frame_cam2 is None:
            return

        os.makedirs("captures", exist_ok=True)
        filename = datetime.now().strftime("captures/%Y%m%d_%H%M%S.jpg")
        cv2.imwrite(filename, self.frame_cam2)

    def change_page(self, index: int) -> None:
        self.stack.setCurrentIndex(index)
