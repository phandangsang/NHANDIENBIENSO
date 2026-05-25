from pathlib import Path
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class Sidebar(QWidget):

    pageChanged = pyqtSignal(int)

    def __init__(self):
        super().__init__()

        self.setObjectName("sidebar")

        css_path = Path(__file__).resolve().parent / "style" / "sidebar.css"
        try:
            with open(css_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            print(f"Khong tim thay file CSS: {css_path}")

        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)

        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title = QLabel("LPR Admin")
        layout.addWidget(title)

        layout.addSpacing(20)

        dashboardBtn = QPushButton("🏠 Bảng điều khiển")
        vehiclesBtn = QPushButton("🚗 Phương tiện")
        usersBtn = QPushButton("👤 Người dùng")
        settingsBtn = QPushButton("⚙ Cài đặt")

        dashboardBtn.clicked.connect(lambda: self.pageChanged.emit(0))
        vehiclesBtn.clicked.connect(lambda: self.pageChanged.emit(1))
        usersBtn.clicked.connect(lambda: self.pageChanged.emit(2))
        settingsBtn.clicked.connect(lambda: self.pageChanged.emit(3))

        layout.addWidget(dashboardBtn)
        layout.addWidget(vehiclesBtn)
        layout.addWidget(usersBtn)
        layout.addWidget(settingsBtn)

        layout.addStretch()