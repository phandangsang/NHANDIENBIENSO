import sys
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from sidebar import Sidebar


class Dashboard(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("LPR Dashboard")
        self.setGeometry(100, 50, 1400, 900)

        self.setStyleSheet("""
            QWidget {
                background-color: #F5F7FB;
                font-family: Segoe UI;
            }

            #sidebar {
                background-color: white;
                border-right: 1px solid #DDE3EA;
            }

            #card {
                background-color: white;
                border: 1px solid #DDE3EA;
                border-radius: 15px;
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

            QTableWidget {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #DDE3EA;
                gridline-color: #EEF2F6;
                font-size: 14px;
            }

            QHeaderView::section {
                background-color: #F9FAFC;
                padding: 10px;
                border: none;
                border-bottom: 1px solid #DDE3EA;
                font-weight: bold;
            }
        """)

        self.initUI()

    def initUI(self):
        mainWidget = QWidget()
        self.setCentralWidget(mainWidget)

        mainLayout = QHBoxLayout(mainWidget)
        mainLayout.setContentsMargins(0, 0, 0, 0)

        sidebar = Sidebar()
        content = self.createContent()

        mainLayout.addWidget(sidebar, 1)
        mainLayout.addWidget(content, 4)

    

    def createContent(self):
        content = QWidget()

        layout = QVBoxLayout(content)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)

        topBar = self.createTopBar()
        layout.addWidget(topBar)

        centerLayout = QHBoxLayout()

        left = self.createCameraCard()
        right = self.createStats()

        centerLayout.addWidget(left, 3)
        centerLayout.addWidget(right, 1)

        layout.addLayout(centerLayout)

        tableTitle = QLabel("Recent Activity")
        tableTitle.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
        """)

        layout.addWidget(tableTitle)

        table = self.createTable()
        layout.addWidget(table)

        return content

    def createTopBar(self):
        widget = QWidget()
        layout = QHBoxLayout(widget)

        titleLayout = QVBoxLayout()

        title = QLabel("System Overview")
        title.setStyleSheet("""
            font-size: 36px;
            font-weight: bold;
        """)

        subtitle = QLabel("Real-time monitoring and analytics")
        subtitle.setStyleSheet("""
            color: gray;
            font-size: 15px;
        """)

        titleLayout.addWidget(title)
        titleLayout.addWidget(subtitle)

        layout.addLayout(titleLayout)
        layout.addStretch()

        dateLabel = QLabel("Oct 24, 2023 - 14:32:05")
        dateLabel.setStyleSheet("""
            background: white;
            border: 1px solid #DDE3EA;
            border-radius: 10px;
            padding: 10px 15px;
        """)

        registerBtn = QPushButton("+ Register Target")
        registerBtn.setStyleSheet("""
            QPushButton {
                background-color: #1D4ED8;
                color: white;
                padding: 12px 20px;
                border-radius: 10px;
                font-weight: bold;
            }
        """)

        layout.addWidget(dateLabel)
        layout.addSpacing(15)
        layout.addWidget(registerBtn)

        return widget

    def createCameraCard(self):
        card = QFrame()
        card.setObjectName("card")

        layout = QVBoxLayout(card)

        header = QLabel("📷 Live Feed: Node Alpha")
        header.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
        """)

        layout.addWidget(header)

        image = QLabel()

        pixmap = QPixmap("road.jpg")

        image.setPixmap(
            pixmap.scaled(
                900,
                500,
                Qt.AspectRatioMode.KeepAspectRatioByExpanding
            )
        )

        image.setMinimumHeight(500)
        image.setStyleSheet("""
            border-radius: 12px;
        """)

        layout.addWidget(image)

        return card

    def createStats(self):
        widget = QWidget()

        layout = QVBoxLayout(widget)
        layout.setSpacing(20)

        stats = [
            ("Total Scans Today", "14,285", "+12% vs yesterday"),
            ("Flagged Vehicles", "23", "Requires immediate review"),
            ("Active Cameras", "12/12", "100% System Uptime")
        ]

        for title, value, sub in stats:
            card = QFrame()
            card.setObjectName("card")

            cardLayout = QVBoxLayout(card)

            t = QLabel(title)
            t.setStyleSheet("""
                font-size: 18px;
                font-weight: bold;
            """)

            v = QLabel(value)
            v.setStyleSheet("""
                font-size: 42px;
                font-weight: bold;
            """)

            s = QLabel(sub)
            s.setStyleSheet("""
                color: gray;
            """)

            cardLayout.addWidget(t)
            cardLayout.addSpacing(10)
            cardLayout.addWidget(v)
            cardLayout.addWidget(s)

            layout.addWidget(card)

        layout.addStretch()

        return widget

    def createTable(self):
        table = QTableWidget()

        table.setRowCount(3)
        table.setColumnCount(6)

        table.setHorizontalHeaderLabels([
            "Image",
            "Plate Number",
            "Timestamp",
            "Location",
            "Status",
            "Action"
        ])

        table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        table.verticalHeader().setVisible(False)
        table.setAlternatingRowColors(True)
        table.setMinimumHeight(300)

        data = [
            ["🚗", "BZT-4521", "14:31:42", "Node Alpha", "Stolen Vehicle", "👁"],
            ["🚘", "XYZ-9876", "14:31:15", "Node Alpha", "Clear", "👁"],
            ["🚐", "LMN-1022", "14:30:58", "Node Beta", "Clear", "👁"]
        ]

        for row in range(len(data)):
            for col in range(len(data[row])):
                item = QTableWidgetItem(data[row][col])

                item.setTextAlignment(
                    Qt.AlignmentFlag.AlignCenter
                )

                table.setItem(row, col, item)

        return table


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = Dashboard()
    window.show()

    sys.exit(app.exec())