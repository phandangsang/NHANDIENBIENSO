from pathlib import Path
from shutil import copy2

from config import ENTRY_IMAGE_DIR, EXIT_IMAGE_DIR, PLATE_IMAGE_DIR
from utils.datetime_utils import get_timestamp_text
from utils.validation import normalize_plate_number


IMAGE_DIRS = {
    "entry": ENTRY_IMAGE_DIR,
    "exit": EXIT_IMAGE_DIR,
    "plate": PLATE_IMAGE_DIR,
}


def save_image(source_path: str, plate_number: str, image_type: str) -> str:
    target_dir = IMAGE_DIRS[image_type]
    target_dir.mkdir(parents=True, exist_ok=True)

    source = Path(source_path)
    plate_number = normalize_plate_number(plate_number)
    target_name = f"{plate_number}_{get_timestamp_text()}{source.suffix}"
    target_path = target_dir / target_name

    copy2(source, target_path)
    return str(target_path)
