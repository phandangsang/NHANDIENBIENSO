import os
from datetime import datetime

import cv2
from PyQt5.QtCore import Qt, QThread, QTimer, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import (
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from .exit_window import ExitWindow
from .recognition_worker import EntryRecognitionService
from .sidebar import Sidebar
from .user_window import UserPage
from .vehicles_window import VehiclesWindow
from models.user_model import (
    create_user,
    delete_user,
    list_users,
    update_password,
    update_user,
)


class DashboardWindow(QMainWindow):
    logout_requested = pyqtSignal()
    entry_scan_requested = pyqtSignal(object, object)

    def __init__(self, user: dict):
        super().__init__()
        self.user = user

        self.setWindowTitle("LPR Dashboard")
        self.resize(1200, 700)

        self.cap1 = None
        self.cap2 = None
        self.frame_cam1 = None
        self.frame_cam2 = None
        self.recognition_busy = False
        self.recognition_thread = None
        self.recognition_service = None

        self.cap1_index = 0
        self.cap2_index = 1

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_camera)

        self._build_ui()
        self._load_styles()
        self._open_cameras()
        self._start_recognition_service()
        self.timer.start(30)

    def closeEvent(self, event):
        self.timer.stop()
        self._stop_workers()
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
        self.page_exit_scan = ExitWindow()
        self.page_vehicles = VehiclesWindow()
        self.page_users = UserPage()
        self._setup_user_page()

        # Keep indexes aligned with ui/sidebar.py (0..3)
        self.stack.addWidget(self.page_dashboard)  # 0
        self.stack.addWidget(self.page_exit_scan)  # 1
        self.stack.addWidget(self.page_vehicles)   # 2
        self.stack.addWidget(self.page_users)      # 3

        self.sidebar.pageChanged.connect(self.change_page)
        self.sidebar.logoutRequested.connect(self.logout_requested.emit)

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

    def _stop_workers(self) -> None:
        if self.recognition_thread is not None and self.recognition_thread.isRunning():
            if self.recognition_service is not None:
                self.recognition_service.shutdown()
            self.recognition_thread.quit()
            self.recognition_thread.wait(3000)
        self.recognition_thread = None
        self.recognition_service = None

    def update_camera(self) -> None:
        if self.cap1 is not None and self.cap1.isOpened():
            ret1, frame1 = self.cap1.read()
            if ret1 and frame1 is not None:
                self.frame_cam1 = frame1.copy()
                self.show_frame(frame1, self.camera_label_1)
                self.page_exit_scan.update_camera_frame(frame1)

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
        frame = self.frame_cam1 if self.frame_cam1 is not None else self.frame_cam2
        if frame is None:
            QMessageBox.warning(self, "Camera", "Chua co hinh anh tu camera nhan dien.")
            return

        if self.recognition_busy:
            return

        self.confirm_btn.setEnabled(False)
        self.confirm_btn.setText("DANG NHAN DIEN...")
        self.plate_label.setText("DANG DOC...")

        self.recognition_busy = True
        self.entry_scan_requested.emit(frame.copy(), self.user.get("id"))

    def _start_recognition_service(self) -> None:
        self.recognition_thread = QThread(self)
        self.recognition_service = EntryRecognitionService()
        self.recognition_service.moveToThread(self.recognition_thread)

        self.recognition_thread.started.connect(self.recognition_service.preload)
        self.entry_scan_requested.connect(self.recognition_service.scan_entry)
        self.recognition_service.ready.connect(self._on_ocr_ready)
        self.recognition_service.preload_failed.connect(self._on_ocr_preload_failed)
        self.recognition_service.failed.connect(self._on_entry_failed)
        self.recognition_service.finished_ok.connect(self._on_entry_recognized)
        self.recognition_service.busy_changed.connect(self._on_recognition_busy_changed)
        self.recognition_thread.start()

    def _on_ocr_ready(self) -> None:
        self.confirm_btn.setToolTip("PaddleOCR da san sang.")

    def _on_ocr_preload_failed(self, message: str) -> None:
        self.confirm_btn.setToolTip(f"OCR chua san sang: {message}")

    def _on_entry_recognized(self, data: dict) -> None:
        plate_number = data.get("plate_number", "--")
        captured_at = data.get("captured_at", "--")
        confidence = data.get("confidence")

        self.plate_label.setText(plate_number)
        self.time_label.setText(captured_at)

        message = f"Da luu xe vao: {plate_number}"
        if confidence is not None:
            message += f"\nDo tin cay: {float(confidence):.2f}"
        QMessageBox.information(self, "Thanh cong", message)

    def _on_entry_failed(self, message: str) -> None:
        self.plate_label.setText("--")
        QMessageBox.warning(self, "Nhan dien that bai", message)
        self._on_recognition_busy_changed(False)

    def _on_recognition_busy_changed(self, is_busy: bool) -> None:
        self.recognition_busy = is_busy
        if is_busy:
            return

        self.confirm_btn.setEnabled(True)
        self.confirm_btn.setText("XAC NHAN")

    def change_page(self, index: int) -> None:
        self.stack.setCurrentIndex(index)

    def _setup_user_page(self) -> None:
        self.page_users.set_permissions(can_manage_users=self._can_manage_users())
        self.page_users.set_callbacks(
            on_add=self._add_user,
            on_edit=self._edit_user,
            on_delete=self._delete_user,
            on_change_password=self._change_user_password,
        )
        self._reload_users()

    def _reload_users(self) -> None:
        try:
            self.page_users.load_users(list_users())
        except Exception as exc:
            print(f"Load users error: {exc}")

    def _can_manage_users(self) -> bool:
        return (self.user.get("role") or "").lower() == "admin"

    def _show_permission_warning(self) -> None:
        QMessageBox.warning(
            self,
            "Khong co quyen",
            "Chi tai khoan admin moi duoc chinh sua thong tin nguoi dung.",
        )

    def _add_user(self, data: dict) -> None:
        if not self._can_manage_users():
            self._show_permission_warning()
            return
        try:
            create_user(
                username=data.get("username", ""),
                password=data.get("password", ""),
                full_name=data.get("full_name", ""),
                role=data.get("role", "staff"),
            )
            self._reload_users()
            QMessageBox.information(self, "Thanh cong", "Da them nguoi dung moi.")
        except Exception as exc:
            print(f"Add user error: {exc}")
            if "Duplicate entry" in str(exc) and "uq_user_username" in str(exc):
                QMessageBox.warning(
                    self,
                    "Them nguoi dung that bai",
                    "Ten dang nhap nay da ton tai. Vui long nhap username khac.",
                )
            else:
                QMessageBox.warning(
                    self,
                    "Them nguoi dung that bai",
                    f"Khong the them nguoi dung.\nLoi: {exc}",
                )

    def _edit_user(self, user_id: int, data: dict) -> None:
        if not self._can_manage_users():
            self._show_permission_warning()
            return
        try:
            updated_user = update_user(user_id, data)
            self.page_users.refresh_user(updated_user)
        except Exception as exc:
            print(f"Edit user error: {exc}")

    def _delete_user(self, user_id: int) -> None:
        if not self._can_manage_users():
            self._show_permission_warning()
            return
        try:
            delete_user(user_id)
            self.page_users.remove_user(user_id)
        except Exception as exc:
            print(f"Delete user error: {exc}")

    def _change_user_password(self, user_id: int, password: str) -> None:
        if not self._can_manage_users():
            self._show_permission_warning()
            return
        try:
            updated_user = update_password(user_id, password)
            self.page_users.refresh_user(updated_user)
        except Exception as exc:
            print(f"Change password error: {exc}")
