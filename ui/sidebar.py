from PyQt6.QtWidgets import *
from PyQt6.QtCore import *


class Sidebar(QWidget):
    def __init__(self):
        super().__init__()

        self.setObjectName("sidebar")

        self.setStyleSheet("""
            #sidebar {
                background-color: white;
                border-right: 1px solid #DDE3EA;
            }

            QPushButton {
                background-color: transparent;
                border: none;
                padding: 12px;
                text-align: left;
                font-size: 15px;
                border-radius: 10px;
            }

            QPushButton:hover {
                background-color: #E8EEFF;
            }

            #activeBtn {
                background-color: #DCE6FF;
                color: #2D5BFF;
                font-weight: bold;
            }
        """)

        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)

        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title = QLabel("LPR Admin")

        title.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #1D4ED8;
        """)

        subtitle = QLabel("Sector 7 Node")
        subtitle.setStyleSheet("color: gray;")

        layout.addWidget(title)
        layout.addWidget(subtitle)

        layout.addSpacing(20)

        menuItems = [
            ("🏠 Dashboard", True),
            ("🚗 Vehicles", True),
            ("👤 User", True),
            ("⚙ Settings", True)
        ]

        for text, active in menuItems:
            btn = QPushButton(text)

            if active:
                btn.setObjectName("activeBtn")

            layout.addWidget(btn)

        layout.addStretch()