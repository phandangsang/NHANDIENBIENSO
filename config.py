from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

ENTRY_IMAGE_DIR = BASE_DIR / "storage" / "entry_images"
EXIT_IMAGE_DIR = BASE_DIR / "storage" / "exit_images"
PLATE_IMAGE_DIR = BASE_DIR / "storage" / "plate_images"

CAMERA_INDEX = 0

# MySQL database config
MYSQL_HOST = "127.0.0.1"
MYSQL_PORT = 3306
MYSQL_USER = "root"
MYSQL_PASSWORD = ""
MYSQL_DATABASE = "license_plate_parking"

# YOLOv8 license plate detector
# - Dat file model (.pt) vao thu muc `weights/` va cap nhat ten file neu can.
YOLO_USE = False
YOLO_MODEL_PATH = BASE_DIR / "weights" / "license_plate_yolov8.pt"
