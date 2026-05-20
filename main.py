from ui.dashboard import Dashboard
from PyQt6.QtWidgets import QApplication
import sys

app = QApplication(sys.argv)

window = Dashboard()
window.show()

sys.exit(app.exec())