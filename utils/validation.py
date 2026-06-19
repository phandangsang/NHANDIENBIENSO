import re


def normalize_plate_number(plate_number: str) -> str:
    normalized = re.sub(r"[^A-Z0-9]", "", plate_number.upper())
    return _extract_plate_candidate(normalized)


def is_valid_plate_number(plate_number: str) -> bool:
    normalized = normalize_plate_number(plate_number)
    if not 7 <= len(normalized) <= 10:
        return False

    vietnam_plate_patterns = (
        # O to/xe may pho bien: 51F97022, 30A88888, 59A112345
        r"^\d{2}[A-Z]{1,2}\d{4,6}$",
        # Mot so bien co chu + so o cum giua: 59A112345
        r"^\d{2}[A-Z]\d[A-Z]?\d{4,5}$",
    )
    return any(re.match(pattern, normalized) for pattern in vietnam_plate_patterns)


def _extract_plate_candidate(text: str) -> str:
    """Trich xuat chuoi bien so hop le tu text OCR co the chua ky tu rac."""
    candidate_patterns = (
        r"\d{2}[A-Z]{1,2}\d{4,6}",
        r"\d{2}[A-Z]\d[A-Z]?\d{4,5}",
    )
    for pattern in candidate_patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0)
    return text
