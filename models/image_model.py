def create_image(
    parking_record_id: int,
    image_path: str,
    image_type: str,
    plate_detected: str | None = None,
    confidence: float | None = None,
) -> int:
    from database.db import execute

    return execute(
        """
        INSERT INTO `images` (
            `parking_record_id`,
            `image_path`,
            `image_type`,
            `plate_detected`,
            `confidence`
        )
        VALUES (%s, %s, %s, %s, %s)
        """,
        (
            parking_record_id,
            image_path,
            image_type,
            plate_detected,
            confidence,
        ),
    )
