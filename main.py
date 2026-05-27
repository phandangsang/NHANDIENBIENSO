import sys
from PyQt5.QtWidgets import QApplication
from ui.dashboard_window import DashboardWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)

    fake_user = {
        "id": 1,
        "username": "admin",
        "full_name": "Nguyễn Văn A",
        "role": "admin"
    }

    w = DashboardWindow(fake_user)

    # 🔥 nếu dashboard có user_page thì inject fake data
    fake_users = [
        {
            "id": 1,
            "username": "admin",
            "full_name": "Nguyễn Văn A",
            "role": "admin",
            "notif": 2,
            "phone": "0901234567",
            "email": "admin@gmail.com",
            "shift": "Ca sáng",
            "stats": {"total": 120, "warning": 5, "denied": 2},
            "recent_scans": [
                {
                    "plate": "51A-12345",
                    "info": "TP.HCM · Xe con",
                    "time": "10:30",
                    "status": "THÔNG QUA"
                }
            ]
        }
    ]

    # ⚠️ tùy dashboard của bạn có user_page không
    w.user_page.load_users(fake_users)

    w.show()
    sys.exit(app.exec_())