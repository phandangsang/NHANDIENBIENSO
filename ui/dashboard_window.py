import os
import cv2
from datetime import datetime

from PyQt5.QtCore import pyqtSignal, Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QFrame,
    QPushButton,
    QStackedWidget,
    QGridLayout,
    QComboBox
)

from .sidebar import Sidebar


class DashboardWindow(QMainWindow):
    logout_requested = pyqtSignal()

    def __init__(self, user: dict):
        super().__init__()

        self.user = user

        self.setWindowTitle("LPR Dashboard")
        self.resize(1200, 700)

        self.cap1_index = 0
        self.cap2_index = 1

        self.cap1 = cv2.VideoCapture(self.cap1_index, cv2.CAP_DSHOW)
        self.cap2 = cv2.VideoCapture(self.cap2_index, cv2.CAP_DSHOW)

        self.frame_cam2 = None

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_camera)
        self.timer.start(30)

        self._build_ui()
        self.load_styles()

    # ================= LOAD CSS =================
    def load_styles(self):
        base_path = os.path.dirname(os.path.abspath(__file__))
        css_path = os.path.join(base_path, "style", "dashboard.qss")

        with open(css_path, "r", encoding="utf-8") as f:
            self.setStyleSheet(f.read())

    # ================= UI =================
    def _build_ui(self):

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.sidebar = Sidebar()
        self.stack = QStackedWidget()

        self.stack.addWidget(self._create_dashboard_page())
        self.stack.addWidget(self._create_simple_page("ENTRY WINDOW"))
        self.stack.addWidget(self._create_simple_page("EXIT WINDOW"))
        self.stack.addWidget(self._create_simple_page("HISTORY WINDOW"))

        self.sidebar.pageChanged.connect(self.change_page)

        main_layout.addWidget(self.sidebar, 1)
        main_layout.addWidget(self.stack, 5)

    # ================= DASHBOARD =================
    def _create_dashboard_page(self):

        page = QWidget()
        main_layout = QVBoxLayout(page)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # ===== CAMERA =====
        camera_layout = QHBoxLayout()

        cam1 = self._create_camera("Camera nhận diện", 0)
        cam2 = self._create_camera("Camera chụp ảnh", 1)

        self.camera_label_1 = cam1["label"]
        self.camera_label_2 = cam2["label"]

        self.cam1_select = cam1["combo"]
        self.cam2_select = cam2["combo"]

        self.cam1_select.currentIndexChanged.connect(self.change_camera_1)
        self.cam2_select.currentIndexChanged.connect(self.change_camera_2)

        camera_layout.addWidget(cam1["frame"])
        camera_layout.addWidget(cam2["frame"])

        # ===== INFO FRAME (GỘP) =====
        self.info_frame = QFrame()
        self.info_frame.setObjectName("info_frame")

        info_layout = QGridLayout(self.info_frame)

        self.plate_label = QLabel("59A-12345")
        self.plate_label.setAlignment(Qt.AlignCenter)
        self.plate_label.setObjectName("plate_label")

        self.time_label = QLabel()
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setObjectName("time_label")

        info_layout.addWidget(self.plate_label, 0, 0)
        info_layout.addWidget(self.time_label, 0, 1)

        # ===== BUTTON =====
        self.confirm_btn = QPushButton("XÁC NHẬN")
        self.confirm_btn.setFixedHeight(50)
        self.confirm_btn.clicked.connect(self.capture_image)

        # ===== ADD =====
        main_layout.addLayout(camera_layout)
        main_layout.addWidget(self.info_frame)
        main_layout.addWidget(self.confirm_btn)

        return page

    # ================= CAMERA COMPONENT =================
    def _create_camera(self, title, default_index):

        frame = QFrame()
        layout = QVBoxLayout(frame)

        top = QHBoxLayout()

        label = QLabel(title)

        combo = QComboBox()
        combo.addItems(["Camera 0", "Camera 1", "Camera 2", "Camera 3"])
        combo.setCurrentIndex(default_index)

        top.addWidget(label)
        top.addStretch()
        top.addWidget(combo)

        cam_label = QLabel()
        cam_label.setFixedSize(500, 300)
        cam_label.setAlignment(Qt.AlignCenter)

        layout.addLayout(top)
        layout.addWidget(cam_label)

        return {
            "frame": frame,
            "label": cam_label,
            "combo": combo
        }

    # ================= CAMERA UPDATE =================
    def update_camera(self):

        if self.cap1.isOpened():
            ret1, frame1 = self.cap1.read()
            if ret1:
                self.show_frame(frame1, self.camera_label_1)
                self.plate_label.setText("59A-12345")

        if self.cap2.isOpened():
            ret2, frame2 = self.cap2.read()
            if ret2:
                self.frame_cam2 = frame2.copy()
                self.show_frame(frame2, self.camera_label_2)

        self.time_label.setText(
            datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        )

    # ================= SHOW FRAME =================
    def show_frame(self, frame, label):

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame.shape

        img = QImage(frame.data, w, h, ch * w, QImage.Format_RGB888)

        pix = QPixmap.fromImage(img)

        label.setPixmap(
            pix.scaled(label.width(), label.height(),
                       Qt.KeepAspectRatio,
                       Qt.SmoothTransformation)
        )

    # ================= CAMERA SWITCH =================
    def change_camera_1(self, index):
        if self.cap1.isOpened():
            self.cap1.release()
        self.cap1 = cv2.VideoCapture(index, cv2.CAP_DSHOW)

    def change_camera_2(self, index):
        if self.cap2.isOpened():
            self.cap2.release()
        self.cap2 = cv2.VideoCapture(index, cv2.CAP_DSHOW)

    # ================= CAPTURE =================
    def capture_image(self):

        if self.frame_cam2 is None:
            return

        os.makedirs("captures", exist_ok=True)

        filename = datetime.now().strftime("captures/%Y%m%d_%H%M%S.jpg")

        cv2.imwrite(filename, self.frame_cam2)

        print("Saved:", filename)

    # ================= SIMPLE PAGE =================
    def _create_simple_page(self, name):
        page = QWidget()
        layout = QVBoxLayout(page)

        label = QLabel(name)
        label.setStyleSheet("font-size:24px;font-weight:bold;")

        layout.addWidget(label)
        layout.addStretch()

        return page

    def change_page(self, index):
        self.stack.setCurrentIndex(index)

    # ================= CLOSE =================
    def closeEvent(self, event):

        if self.cap1.isOpened():
            self.cap1.release()

        if self.cap2.isOpened():
            self.cap2.release()

        event.accept()