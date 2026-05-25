# License Plate Parking

Ung dung Python nhan dien bien so xe ra vao bai do xe va luu lich su vao he thong.

## Chuc nang chinh

- Dang nhap nguoi dung.
- Nhan dien bien so xe tu anh/camera.
- Ghi nhan xe vao bai.
- Ghi nhan xe ra bai.
- Luu anh xe va anh bien so.
- Xem lich su xe ra vao.

## Cau truc chinh

- `database/`: database MySQL va file tao bang.
- `models/`: thao tac truc tiep voi database.
- `services/`: xu ly nghiep vu xe vao/ra.
- `recognition/`: xu ly anh va OCR bien so.
- `ui/`: giao dien chuong trinh.
- `storage/`: luu anh xe va bien so.
- `utils/`: ham tien ich dung chung.

## Vai tro cua tung thu muc va file

```text
license_plate_parking/
|-- main.py
|-- config.py
|-- requirements.txt
|-- README.md
|-- database/
|-- models/
|-- services/
|-- recognition/
|-- ui/
|-- storage/
`-- utils/
```

### Thu muc goc

| File | Vai tro |
| --- | --- |
| `main.py` | File chay chinh cua chuong trinh. Khi khoi dong ung dung, chuong trinh bat dau tu file nay. |
| `config.py` | Luu cau hinh dung chung nhu duong dan database, thu muc luu anh va camera mac dinh. |
| `requirements.txt` | Luu danh sach thu vien Python can cai dat cho du an. |
| `README.md` | Mo ta du an, chuc nang, cach cai dat, cach chay va cau truc thu muc. |

### Thu muc `database/`

| File | Vai tro |
| --- | --- |
| `schema.sql` | Chua cau lenh SQL tao cac bang `user`, `vehicle`, `parking_records`, `images`. |
| `db.py` | Chua ham ket noi database va ham khoi tao database. |
| `README_DATABASE.md` | Giai thich rieng ve cau truc database va luong du lieu xe vao/ra. |

### Thu muc `models/`

Thu muc nay chua cac file thao tac truc tiep voi tung bang trong database.

| File | Vai tro |
| --- | --- |
| `user_model.py` | Tim kiem thong tin nguoi dung, phuc vu chuc nang dang nhap. |
| `vehicle_model.py` | Tim xe theo bien so, them xe moi neu bien so chua ton tai. |
| `parking_record_model.py` | Tao ban ghi xe vao, tim xe dang trong bai, cap nhat xe ra va lay lich su. |
| `image_model.py` | Luu duong dan anh va thong tin nhan dien vao bang `images`. |
| `__init__.py` | Danh dau `models` la mot package Python. |

### Thu muc `services/`

Thu muc nay chua logic nghiep vu cua he thong, la tang trung gian giua giao dien, nhan dien va database.

| File | Vai tro |
| --- | --- |
| `auth_service.py` | Xu ly dang nhap nguoi dung. |
| `parking_service.py` | Xu ly luong xe vao va xe ra: nhan bien so, tao/cap nhat ban ghi, luu anh. |
| `image_service.py` | Xu ly luu file anh vao dung thu muc va tao ten file anh. |
| `__init__.py` | Danh dau `services` la mot package Python. |

### Thu muc `recognition/`

Thu muc nay chua phan xu ly anh va nhan dien bien so xe.

| File | Vai tro |
| --- | --- |
| `image_processing.py` | Tien xu ly anh bang OpenCV, vi du chuyen anh xam, lam mo, loc nhieu. |
| `plate_detector.py` | Phat hien va cat vung bien so xe tu anh goc. |
| `ocr_reader.py` | Doc ky tu tren bien so bang OCR va tra ve bien so nhan dien duoc. |
| `__init__.py` | Danh dau `recognition` la mot package Python. |

### Thu muc `ui/`

Thu muc nay chua cac file giao dien nguoi dung.

| File | Vai tro |
| --- | --- |
| `app.py` | Khoi tao ung dung, goi ham tao database va mo giao dien chinh. |
| `login_window.py` | Man hinh dang nhap. |
| `dashboard_window.py` | Man hinh tong quan, hien thi thong tin xe trong bai va lich su gan day. |
| `entry_window.py` | Man hinh xu ly xe vao bai. |
| `exit_window.py` | Man hinh xu ly xe ra bai. |
| `history_window.py` | Man hinh xem lich su xe ra/vao. |
| `__init__.py` | Danh dau `ui` la mot package Python. |

### Thu muc `storage/`

Thu muc nay luu cac anh duoc chup trong qua trinh xe vao/ra. Database chi luu duong dan anh, khong luu truc tiep file anh.

| Thu muc | Vai tro |
| --- | --- |
| `entry_images/` | Luu anh xe khi vao bai. |
| `exit_images/` | Luu anh xe khi ra bai. |
| `plate_images/` | Luu anh bien so da duoc cat tu anh goc. |

### Thu muc `utils/`

Thu muc nay chua cac ham tien ich dung chung cho nhieu phan cua chuong trinh.

| File | Vai tro |
| --- | --- |
| `datetime_utils.py` | Xu ly ngay gio, tao chuoi thoi gian de dat ten file anh. |
| `validation.py` | Chuan hoa va kiem tra dinh dang bien so xe. |
| `__init__.py` | Danh dau `utils` la mot package Python. |

## Luong hoat dong tong quat

```text
ui/
-> services/
-> recognition/
-> models/
-> database/
-> storage/
```

Giai thich:

1. Nguoi dung thao tac tren giao dien trong `ui/`.
2. Giao dien goi cac ham nghiep vu trong `services/`.
3. Neu can nhan dien bien so, `services/` goi cac ham trong `recognition/`.
4. Sau khi co bien so, `services/` goi `models/` de luu hoac doc du lieu.
5. `models/` ket noi MySQL thong qua `database/db.py`.
6. Anh xe va anh bien so duoc luu trong `storage/`.

## Cai dat

```bash
pip install -r requirements.txt
```

## Cau hinh MySQL

- Tao MySQL database va user (hoac dung `root`).
- Chinh sua thong tin ket noi trong `config.py`: `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE`.
    python -c "from database.db import init_database; init_database(); print('OK')"
## Chay chuong trinh

```bash
python main.py
```

## Bat YOLOv8 (Object Detection) de cat vung bien so

1. Cai thu vien:

```bash
pip install ultralytics
```

2. Dat model YOLOv8 (file `.pt`) vao `weights/` (vi du `weights/license_plate_yolov8.pt`).
3. Mo `config.py` va set:

```python
YOLO_USE = True
```
'''giao dien chay app 
vao python 
mo terminal
python -m pip install PyQt5
