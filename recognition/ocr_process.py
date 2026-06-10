from __future__ import annotations

import contextlib
import json
import os
import re
import sys
from pathlib import Path


_PROJECT_DIR = Path(__file__).resolve().parents[1]
_PADDLEX_CACHE_DIR = _PROJECT_DIR / "storage" / "paddlex_cache"
_MODEL_CACHE_DIR = _PROJECT_DIR / "storage" / "model_cache"

os.environ["FLAGS_enable_pir_api"] = "0"
os.environ["FLAGS_enable_pir_in_executor"] = "0"
os.environ["FLAGS_use_mkldnn"] = "0"
os.environ["FLAGS_enable_onednn"] = "0"
os.environ["FLAGS_use_onednn"] = "0"
os.environ["ONEDNN_VERBOSE"] = "0"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ.setdefault("PADDLE_PDX_CACHE_HOME", str(_PADDLEX_CACHE_DIR))
os.environ.setdefault("PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK", "True")
os.environ.setdefault("MODELSCOPE_CACHE", str(_MODEL_CACHE_DIR / "modelscope"))
os.environ.setdefault("HF_HOME", str(_MODEL_CACHE_DIR / "huggingface"))

PROTOCOL_OUT = sys.stdout
sys.stdout = sys.stderr


def main() -> None:
    try:
        reader = _create_reader()
    except Exception as exc:
        _write({"success": False, "error": str(exc)})
        return

    for line in sys.stdin:
        try:
            request = json.loads(line)
            action = request.get("action")

            if action == "ping":
                _write({"success": True, "ready": True})
                continue

            if action != "ocr":
                _write({"success": False, "error": "Lenh OCR khong hop le."})
                continue

            text, confidence = _read_plate_text(reader, request.get("image_path"))
            _write({"success": True, "text": text, "confidence": confidence})
        except Exception as exc:
            _write({"success": False, "error": str(exc)})


def _create_reader():
    with contextlib.redirect_stdout(sys.stderr):
        from paddleocr import PaddleOCR

        try:
            return PaddleOCR(
                use_doc_orientation_classify=False,
                use_doc_unwarping=False,
                use_textline_orientation=False,
                ocr_version="PP-OCRv4",
                lang="en",
                enable_mkldnn=False,
                cpu_threads=1,
            )
        except TypeError:
            return PaddleOCR(
                use_doc_orientation_classify=False,
                use_doc_unwarping=False,
                use_angle_cls=False,
                ocr_version="PP-OCRv4",
                lang="en",
                enable_mkldnn=False,
                cpu_threads=1,
            )


def _read_plate_text(reader, image_path: str | None) -> tuple[str, float]:
    if not image_path:
        return "", 0.0

    with contextlib.redirect_stdout(sys.stderr):
        if hasattr(reader, "predict"):
            result = reader.predict(image_path)
        else:
            result = reader.ocr(image_path)

    candidates = _collect_candidates(result)
    return _merge_plate_candidates(candidates)


def _collect_candidates(result):
    candidates = []

    def walk(value):
        if value is None:
            return

        if isinstance(value, dict):
            texts = value.get("rec_texts") or value.get("texts")
            scores = value.get("rec_scores") or value.get("scores")
            if texts:
                boxes = value.get("rec_boxes")
                polys = value.get("rec_polys") or value.get("dt_polys")
                for index, text in enumerate(texts):
                    score = 0.0
                    if scores and index < len(scores):
                        score = _to_float(scores[index])
                    position = _get_text_position(index, boxes, polys)
                    candidates.append(
                        {
                            "text": str(text),
                            "score": score,
                            "x": position["x"],
                            "y": position["y"],
                            "height": position["height"],
                            "order": len(candidates),
                        }
                    )
                return

            for item in value.values():
                walk(item)
            return

        if isinstance(value, tuple) and len(value) >= 2 and isinstance(value[0], str):
            candidates.append(
                {
                    "text": value[0],
                    "score": _to_float(value[1]),
                    "x": None,
                    "y": None,
                    "height": None,
                    "order": len(candidates),
                }
            )
            return

        if isinstance(value, (list, tuple)):
            for item in value:
                walk(item)

    walk(result)
    return candidates


def _merge_plate_candidates(candidates) -> tuple[str, float]:
    items = []
    for candidate in candidates:
        text = _normalize_plate_text(candidate.get("text", ""))
        if not text:
            continue

        items.append(
            {
                **candidate,
                "text": text,
                "score": _to_float(candidate.get("score")),
            }
        )

    if not items:
        return "", 0.0

    if not any(item.get("y") is not None for item in items):
        text = "".join(item["text"] for item in items)
        score = _average_score(items)
        return text, score

    lines = _group_candidates_by_line(items)
    line_texts = []
    line_scores = []

    for line in lines:
        line.sort(key=lambda item: _sort_value(item.get("x"), item.get("order")))
        line_texts.append("".join(item["text"] for item in line))
        line_scores.extend(item["score"] for item in line)

    plate_text = "".join(line_texts)
    confidence = sum(line_scores) / len(line_scores) if line_scores else 0.0
    return plate_text, confidence


def _group_candidates_by_line(items):
    sorted_items = sorted(
        items,
        key=lambda item: (
            _sort_value(item.get("y"), item.get("order")),
            _sort_value(item.get("x"), item.get("order")),
        ),
    )
    lines = []

    for item in sorted_items:
        y = item.get("y")
        height = item.get("height") or 20
        tolerance = max(12, height * 0.6)

        matched_line = None
        for line in lines:
            line_y = sum(i.get("y") or 0 for i in line) / len(line)
            if y is not None and abs(y - line_y) <= tolerance:
                matched_line = line
                break

        if matched_line is None:
            lines.append([item])
        else:
            matched_line.append(item)

    return lines


def _get_text_position(index: int, boxes, polys) -> dict:
    if boxes is not None and index < len(boxes):
        return _position_from_box(boxes[index])

    if polys is not None and index < len(polys):
        return _position_from_poly(polys[index])

    return {"x": None, "y": None, "height": None}


def _position_from_box(box) -> dict:
    try:
        values = [float(v) for v in list(box)]
        if len(values) >= 4:
            x1, y1, x2, y2 = values[:4]
            return {
                "x": (x1 + x2) / 2,
                "y": (y1 + y2) / 2,
                "height": abs(y2 - y1),
            }
    except Exception:
        pass

    return {"x": None, "y": None, "height": None}


def _position_from_poly(poly) -> dict:
    try:
        points = list(poly)
        xs = [float(point[0]) for point in points]
        ys = [float(point[1]) for point in points]
        return {
            "x": sum(xs) / len(xs),
            "y": sum(ys) / len(ys),
            "height": max(ys) - min(ys),
        }
    except Exception:
        return {"x": None, "y": None, "height": None}


def _average_score(items) -> float:
    scores = [item["score"] for item in items]
    return sum(scores) / len(scores) if scores else 0.0


def _sort_value(value, fallback):
    return value if value is not None else fallback


def _normalize_plate_text(text: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", str(text).upper())


def _to_float(value) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _write(response: dict) -> None:
    PROTOCOL_OUT.write(json.dumps(response, ensure_ascii=False) + "\n")
    PROTOCOL_OUT.flush()


if __name__ == "__main__":
    main()
