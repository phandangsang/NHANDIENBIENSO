# PARKING - License Plate Recognition Parking App

Ung dung desktop Python ho tro nhan dien bien so xe ra vao bai do xe. He thong dung camera de chup khung hinh, nhan dien bien so, luu thong tin xe vao/ra vao MySQL va cho phep quan ly nguoi dung theo phan quyen.

## Muc tieu du an

- Dang nhap he thong bang tai khoan admin/staff.
- Phan quyen nguoi dung: admin duoc quan ly user, staff chi thao tac nghiep vu.
- Quet bien so xe vao bai.
- Quet bien so xe ra bai va doi chieu voi xe dang trong bai.
- Luu lich su xe vao/ra vao database.
- Luu anh chup khi xe vao/ra de doi chieu.
- Quan ly danh sach xe va danh sach nguoi dung.

Du an khong xu ly tinh tien gui xe.

## Cong nghe su dung

| Thanh phan | Cong nghe |
| --- | --- |
| Ngon ngu | Python |
| Giao dien | PyQt5 |
| Database | MySQL, co the chay bang XAMPP |
| Ket noi database | mysql-connector-python |
| Xu ly anh/camera | OpenCV |
| Nhan dien vung bien so | YOLOv8, thu vien ultralytics |
| OCR doc ky tu bien so | PaddleOCR |
| Luu anh | Thu muc local `storage/` |

## Chuc nang chinh

### Dang nhap va phan quyen

- `admin`: quan ly nguoi dung, sua thong tin user, doi mat khau, xoa user, xem danh sach xe, quet xe vao/ra.
- `staff`: quet xe vao/ra, xem danh sach xe, khong duoc chinh sua thong tin nguoi dung.

Tai khoan mac dinh duoc tao khi khoi tao database:

```text
username: admin
password: admin123
role: admin
```

### Quet xe vao

Luong xu ly:

```text
Camera -> chup anh tinh -> YOLO cat vung bien so -> PaddleOCR doc bien so -> luu DB -> luu anh
```

OCR khong chay lien tuc tren tung frame, ma chi chay khi nguoi dung bam nut nhan dien/xac nhan. Cach nay giup giao dien bot lag.

### Quet xe ra

Luong xu ly:

```text
Camera -> nhan dien bien so xe ra -> tim xe dang trong bai -> cap nhat exit_time -> chuyen status thanh out
```

Neu bien so khong co ban ghi xe dang trong bai, he thong se bao khong tim thay xe phu hop.

## Database

Database su dung MySQL, ten mac dinh:

```text
license_plate_parking
```

Thong tin ket noi nam trong [config.py](A:/PYTHON!/config.py):

```python
MYSQL_HOST = "127.0.0.1"
MYSQL_PORT = 3306
MYSQL_USER = "root"
MYSQL_PASSWORD = ""
MYSQL_DATABASE = "license_plate_parking"
```

### Cac bang chinh

| Bang | Vai tro |
| --- | --- |
| `user` | Luu tai khoan dang nhap, ho ten, so dien thoai va vai tro admin/staff. |
| `vehicle` | Luu thong tin xe theo bien so. |
| `parking_records` | Luu moi luot xe vao/ra bai. |
| `images` | Luu duong dan anh chup khi xe vao/ra va thong tin bien so nhan dien. |

### Bang `user`

| Cot | Vai tro |
| --- | --- |
| `id` | Khoa chinh. |
| `username` | Ten dang nhap, khong duoc trung. |
| `password` | Mat khau. |
| `full_name` | Ho ten nguoi dung. |
| `phone` | So dien thoai. |
| `role` | Vai tro: `admin` hoac `staff`. |
| `created_at` | Thoi gian tao tai khoan. |

## Cau truc thu muc

```text
PARKING/
|-- main.py
|-- config.py
|-- requirements.txt
|-- README.md
|-- database/
|-- models/
|-- services/
|-- recognition/
|-- ui/
|   |-- style/
|-- weights/
|-- storage/
|-- captures/
`-- utils/
```

## Vai tro tung thu muc va file

### Thu muc goc

| File | Vai tro |
| --- | --- |
| [main.py](A:/PYTHON!/main.py) | File chay chinh cua ung dung. |
| [config.py](A:/PYTHON!/config.py) | Cau hinh database, camera, duong dan luu anh va model YOLO. |
| [requirements.txt](A:/PYTHON!/requirements.txt) | Danh sach thu vien can cai dat. |
| [README.md](A:/PYTHON!/README.md) | Tai lieu mo ta du an va cach chay. |
| [test_camera.py](A:/PYTHON!/test_camera.py) | File kiem tra cac camera OpenCV nhan duoc. |

### `database/`

| File | Vai tro |
| --- | --- |
| [database/db.py](A:/PYTHON!/database/db.py) | Ket noi MySQL, khoi tao database, ham query chung. |
| [database/schema.sql](A:/PYTHON!/database/schema.sql) | Cau lenh tao bang `user`, `vehicle`, `parking_records`, `images`. |
| [database/README_DATABASE.md](A:/PYTHON!/database/README_DATABASE.md) | Tai lieu rieng ve database. |

### `models/`

| File | Vai tro |
| --- | --- |
| [models/user_model.py](A:/PYTHON!/models/user_model.py) | Them, sua, xoa, tim va liet ke nguoi dung. |
| [models/vehicle_model.py](A:/PYTHON!/models/vehicle_model.py) | Tim hoac tao xe theo bien so. |
| [models/parking_record_model.py](A:/PYTHON!/models/parking_record_model.py) | Tao ban ghi xe vao, cap nhat xe ra, lay lich su. |
| [models/image_model.py](A:/PYTHON!/models/image_model.py) | Luu thong tin anh vao bang `images`. |

### `services/`

| File | Vai tro |
| --- | --- |
| [services/auth_service.py](A:/PYTHON!/services/auth_service.py) | Xu ly dang nhap. |
| [services/entry_service.py](A:/PYTHON!/services/entry_service.py) | Xu ly nghiep vu xe vao bai. |
| [services/exit_service.py](A:/PYTHON!/services/exit_service.py) | Xu ly nghiep vu xe ra bai. |
| [services/parking_service.py](A:/PYTHON!/services/parking_service.py) | Cac ham nghiep vu chung cho ghi nhan xe. |

### `recognition/`

| File | Vai tro |
| --- | --- |
| [recognition/yolo_plate_detector.py](A:/PYTHON!/recognition/yolo_plate_detector.py) | Dung YOLOv8 de tim va cat vung bien so. |
| [recognition/plate_detector.py](A:/PYTHON!/recognition/plate_detector.py) | Xu ly phat hien/cat bien so theo logic du phong. |
| [recognition/ocr_reader.py](A:/PYTHON!/recognition/ocr_reader.py) | Goi OCR de doc bien so. |
| [recognition/ocr_process.py](A:/PYTHON!/recognition/ocr_process.py) | Chay PaddleOCR o process rieng. |
| [recognition/entry_recognizer.py](A:/PYTHON!/recognition/entry_recognizer.py) | Nhan dien bien so cho luong xe vao. |
| [recognition/exit_recognizer.py](A:/PYTHON!/recognition/exit_recognizer.py) | Nhan dien bien so cho luong xe ra. |

### `ui/`

| File | Vai tro |
| --- | --- |
| [ui/login_window.py](A:/PYTHON!/ui/login_window.py) | Giao dien dang nhap. |
| [ui/dashboard_window.py](A:/PYTHON!/ui/dashboard_window.py) | Man hinh chinh, bang dieu khien va quet xe vao. |
| [ui/exit_window.py](A:/PYTHON!/ui/exit_window.py) | Giao dien quet xe ra. |
| [ui/vehicles_window.py](A:/PYTHON!/ui/vehicles_window.py) | Giao dien danh sach xe. |
| [ui/user_window.py](A:/PYTHON!/ui/user_window.py) | Giao dien danh sach va quan ly nguoi dung. |
| [ui/sidebar.py](A:/PYTHON!/ui/sidebar.py) | Thanh menu ben trai. |
| [ui/entry_scan_worker.py](A:/PYTHON!/ui/entry_scan_worker.py) | Worker chay ngam cho nhan dien xe vao de UI khong bi treo. |
| [ui/exit_scan_worker.py](A:/PYTHON!/ui/exit_scan_worker.py) | Worker chay ngam cho nhan dien xe ra. |

### `ui/style/`

| File | Vai tro |
| --- | --- |
| [ui/style/loginstyle.css](A:/PYTHON!/ui/style/loginstyle.css) | Giao dien man hinh dang nhap. |
| [ui/style/dashboard.qss](A:/PYTHON!/ui/style/dashboard.qss) | Giao dien dashboard. |
| [ui/style/sidebar.css](A:/PYTHON!/ui/style/sidebar.css) | Giao dien menu ben trai. |
| [ui/style/user.css](A:/PYTHON!/ui/style/user.css) | Giao dien trang nguoi dung. |
| [ui/style/vehicles.css](A:/PYTHON!/ui/style/vehicles.css) | Giao dien danh sach xe. |
| [ui/style/exit.css](A:/PYTHON!/ui/style/exit.css) | Giao dien quet xe ra. |

### `weights/`

| File | Vai tro |
| --- | --- |
| [weights/license_plate_yolov8.pt](A:/PYTHON!/weights/license_plate_yolov8.pt) | Model YOLOv8 nhan dien vung bien so. |
| [weights/README.md](A:/PYTHON!/weights/README.md) | Ghi chu cach dat file model. |

### `storage/` va `captures/`

| Thu muc | Vai tro |
| --- | --- |
| `storage/entry_images/` | Luu anh khi xe vao bai. |
| `storage/exit_images/` | Luu anh khi xe ra bai. |
| `storage/plate_images/` | Luu anh bien so da cat. |
| `captures/` | Luu anh chup/test tu camera. |

### `utils/`

| File | Vai tro |
| --- | --- |
| [utils/datetime_utils.py](A:/PYTHON!/utils/datetime_utils.py) | Xu ly ngay gio va ten file theo thoi gian. |
| [utils/validation.py](A:/PYTHON!/utils/validation.py) | Chuan hoa va kiem tra bien so. |

## Cai dat moi truong

Nen tao moi truong ao truoc khi cai thu vien:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

Neu bi loi quyen khi cai thu vien tren Windows, co the dung:

```powershell
pip install --user -r requirements.txt
```

## Chay database bang XAMPP

1. Mo XAMPP Control Panel.
2. Bam Start o module MySQL.
3. Mo phpMyAdmin: `http://localhost/phpmyadmin`.
4. Kiem tra database `license_plate_parking`.

Neu database chua co, ung dung se tu tao khi chay. Co the khoi tao thu cong bang lenh:

```powershell
python -B -c "from database.db import init_database; init_database(); print('OK')"
```

## Chay ung dung

```powershell
python main.py
```

Sau khi chay:

1. Dang nhap bang tai khoan `admin / admin123`.
2. Vao Bang dieu khien de quet xe vao.
3. Vao Quet xe ra de xu ly xe ra bai.
4. Vao Danh sach xe de xem lich su xe.
5. Vao Nguoi dung de quan ly user neu dang nhap bang admin.

## Kiem tra camera

Chay:

```powershell
python test_camera.py
```

Neu dung dien thoai lam webcam bang DroidCam, can mo DroidCam Client truoc, sau do chon dung camera index trong giao dien hoac trong `config.py`.

## Bat/tat YOLO

YOLO duoc dung de tim dung vung bien so trong anh. Sau khi YOLO cat vung bien so, PaddleOCR moi doc ky tu trong vung do. Cach nay giup tranh viec OCR doc nham chu khac trong khung hinh.

### Cai dat YOLOv8

Thu vien YOLOv8 nam trong package `ultralytics`. Neu da cai bang `requirements.txt` thi khong can cai lai:

```powershell
pip install ultralytics
```

Kiem tra da cai thanh cong:

```powershell
python -c "from ultralytics import YOLO; print('YOLO OK')"
```

### Dat file model YOLO

Co the lay model YOLO da train san tu repo:

[MagicXuanTung/Yolov8-Detect-Vietnamese-license-plates-and-characters](https://github.com/MagicXuanTung/Yolov8-Detect-Vietnamese-license-plates-and-characters)

Repo nay co thu muc `YOLO-Weights`, dung de chua cac file model YOLO. Cach lam:

1. Mo link repo tren GitHub.
2. Vao thu muc `YOLO-Weights`.
3. Tai file model `.pt`, vi du `license_plate_detector.pt` hoac file `.pt` tuong duong.
4. Copy file `.pt` do vao thu muc `weights/` cua du an nay.
5. Doi ten file thanh `license_plate_yolov8.pt` hoac sua lai duong dan trong `config.py`.

Neu muon clone repo ve may:

```powershell
git clone https://github.com/MagicXuanTung/Yolov8-Detect-Vietnamese-license-plates-and-characters.git
```

Sau khi clone, chi can lay file `.pt` trong thu muc `YOLO-Weights` va copy sang du an nay. Khong can copy toan bo source code cua repo vao app.

Tao thu muc `weights` neu chua co:

```powershell
mkdir weights
```

Dat file model `.pt` vao thu muc [weights](A:/PYTHON!/weights). Vi du:

```text
weights/license_plate_yolov8.pt
```

Trong [config.py](A:/PYTHON!/config.py), cau hinh:

```python
YOLO_USE = True
YOLO_MODEL_PATH = BASE_DIR / "weights" / "license_plate_yolov8.pt"
```

Neu file model cua ban co ten khac, vi du `best.pt`, sua lai:

```python
YOLO_MODEL_PATH = BASE_DIR / "weights" / "best.pt"
```

### Kiem tra nhanh file model

Chay lenh:

```powershell
python -c "from ultralytics import YOLO; model = YOLO('weights/license_plate_yolov8.pt'); print(model.names)"
```

Neu lenh in ra danh sach class cua model la YOLO da load duoc.

### Loi thuong gap

| Loi | Cach xu ly |
| --- | --- |
| `No module named ultralytics` | Chay `pip install ultralytics`. |
| `FileNotFoundError` voi file `.pt` | Kiem tra file model da nam dung trong `weights/` chua. |
| YOLO khong tim thay bien so | Model `.pt` co the khong phu hop bien so Viet Nam, can dung model train cho license plate. |
| App cham khi nhan dien | Chi nen bam nhan dien khi xe dung yen, khong OCR lien tuc theo tung frame. |

## Ghi chu ve hieu nang

- Khong nen OCR realtime lien tuc tren tung frame vi se gay lag.
- Nen cho camera hien thi lien tuc, chi chup anh va OCR khi xe dung tai barrier.
- PaddleOCR va YOLO nen duoc load mot lan, sau do worker chay ngam de giao dien PyQt5 khong bi do.
- Anh chup can ro, bien so nam gan giua khung hinh de ket qua OCR tot hon.

## Trang thai hien tai

Da co:

- Dang nhap.
- Phan quyen admin/staff.
- Quan ly nguoi dung.
- Quan ly danh sach xe.
- Quet xe vao.
- Quet xe ra.
- MySQL database.
- YOLOv8 va PaddleOCR.

Co the cai thien them:

- Ma hoa mat khau thay vi luu plain text.
- Giao dien thong bao loi than thien hon.
- Them thong ke so xe trong bai theo ngay.
- Cai thien model YOLO/OCR de nhan dien bien so Viet Nam on dinh hon.
- Dong goi app thanh file `.exe`.
