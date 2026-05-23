from __future__ import annotations

from pathlib import Path
from typing import Any

from config import MYSQL_DATABASE, MYSQL_HOST, MYSQL_PASSWORD, MYSQL_PORT, MYSQL_USER


def get_connection(database: str | None = None):
    import mysql.connector

    return mysql.connector.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=database,
        autocommit=True,
        use_pure=True,  # Tránh crash C extension trên Python 3.13
    )


def init_database() -> None:
    schema_path = Path(__file__).resolve().parent / "schema.sql"
    schema = schema_path.read_text(encoding="utf-8")

    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS `{MYSQL_DATABASE}` "
            "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
        cursor.close()

    with get_connection(MYSQL_DATABASE) as connection:
        cursor = connection.cursor()
        for statement in _split_sql(schema):
            cursor.execute(statement)
        cursor.close()


def fetch_one(query: str, params: tuple[Any, ...] = ()):
    with get_connection(MYSQL_DATABASE) as connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params)
        row = cursor.fetchone()
        cursor.close()
        return row


def fetch_all(query: str, params: tuple[Any, ...] = ()):
    with get_connection(MYSQL_DATABASE) as connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params)
        rows = cursor.fetchall()
        cursor.close()
        return rows


def execute(query: str, params: tuple[Any, ...] = ()) -> int:
    with get_connection(MYSQL_DATABASE) as connection:
        cursor = connection.cursor()
        cursor.execute(query, params)
        lastrowid = cursor.lastrowid or 0
        cursor.close()
        return int(lastrowid)


def _split_sql(schema: str):
    # Simple splitter for our schema.sql: split by semicolon, ignore empty parts.
    parts = []
    for part in schema.split(";"):
        statement = part.strip()
        if statement:
            parts.append(statement)
    return parts
