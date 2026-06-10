import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from threading import Lock

import cv2


_OCR_PROCESS = None
_OCR_LOCK = Lock()


def get_ocr_process():
    """Return one shared PaddleOCR subprocess for the whole app."""
    global _OCR_PROCESS

    if _OCR_PROCESS is not None and _OCR_PROCESS.poll() is None:
        return _OCR_PROCESS

    with _OCR_LOCK:
        if _OCR_PROCESS is not None and _OCR_PROCESS.poll() is None:
            return _OCR_PROCESS

        script_path = Path(__file__).resolve().parent / "ocr_process.py"
        env = os.environ.copy()
        env.update(
            {
                "FLAGS_enable_pir_api": "0",
                "FLAGS_enable_pir_in_executor": "0",
                "FLAGS_use_mkldnn": "0",
                "FLAGS_enable_onednn": "0",
                "FLAGS_use_onednn": "0",
                "ONEDNN_VERBOSE": "0",
                "OMP_NUM_THREADS": "1",
                "KMP_DUPLICATE_LIB_OK": "TRUE",
            }
        )
        _OCR_PROCESS = subprocess.Popen(
            [sys.executable, "-B", str(script_path)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            encoding="utf-8",
            bufsize=1,
            env=env,
        )
        _send_request(_OCR_PROCESS, {"action": "ping"})
        return _OCR_PROCESS


def warm_up_ocr_reader() -> None:
    """Start the OCR subprocess and load PaddleOCR once."""
    get_ocr_process()


def stop_ocr_process() -> None:
    global _OCR_PROCESS

    process = _OCR_PROCESS
    _OCR_PROCESS = None
    if process is None or process.poll() is not None:
        return

    try:
        process.terminate()
        process.wait(timeout=3)
    except Exception:
        try:
            process.kill()
        except Exception:
            pass


def read_plate_text(plate_image):
    """Read plate text by sending the cropped plate image to the OCR subprocess."""
    process = get_ocr_process()
    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
            temp_path = temp_file.name

        cv2.imwrite(temp_path, plate_image)
        response = _send_request(process, {"action": "ocr", "image_path": temp_path})
        return response.get("text", ""), float(response.get("confidence") or 0.0)
    finally:
        if temp_path:
            try:
                Path(temp_path).unlink(missing_ok=True)
            except Exception:
                pass


def _send_request(process, payload: dict) -> dict:
    if process.stdin is None or process.stdout is None:
        raise RuntimeError("OCR process khong san sang.")

    process.stdin.write(json.dumps(payload, ensure_ascii=False) + "\n")
    process.stdin.flush()

    line = process.stdout.readline()
    if not line:
        raise RuntimeError("OCR process da dung dot ngot.")

    response = json.loads(line)
    if not response.get("success"):
        raise RuntimeError(response.get("error") or "OCR that bai.")

    return response
