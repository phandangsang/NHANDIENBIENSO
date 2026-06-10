import re


def normalize_plate_number(plate_number: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", plate_number.upper())


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
