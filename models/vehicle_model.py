def find_by_plate_number(plate_number: str):
    from database.db import fetch_one

    return fetch_one(
        "SELECT * FROM `vehicle` WHERE `plate_number` = %s",
        (plate_number,),
    )


def create_vehicle(plate_number: str, vehicle_type: str = "car") -> int:
    from database.db import execute

    return execute(
        "INSERT INTO `vehicle` (`plate_number`, `vehicle_type`) VALUES (%s, %s)",
        (plate_number, vehicle_type),
    )


def get_or_create_vehicle(plate_number: str, vehicle_type: str = "car") -> int:
    vehicle = find_by_plate_number(plate_number)
    if vehicle:
        return int(vehicle["id"])

    return create_vehicle(plate_number, vehicle_type)
