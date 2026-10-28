"""Acceso a datos: una función por operación, con SQL parametrizado."""

from collections.abc import Sequence

import pyodbc

from backend.database import get_connection

TABLE = "dbo.Paciente"
COLUMNS = "dni, nombre, apellido"

SELECT_ALL_SQL = f"SELECT {COLUMNS} FROM {TABLE} ORDER BY apellido, nombre"
SELECT_ONE_SQL = f"SELECT {COLUMNS} FROM {TABLE} WHERE dni = ?"
INSERT_SQL = f"INSERT INTO {TABLE} ({COLUMNS}) VALUES (?, ?, ?)"
UPDATE_SQL = f"UPDATE {TABLE} SET nombre = ?, apellido = ? WHERE dni = ?"
DELETE_SQL = f"DELETE FROM {TABLE} WHERE dni = ?"


class DuplicateKeyError(Exception):
    """La base de datos rechazó la escritura por una clave duplicada."""


def _to_dict(row: Sequence[object] | pyodbc.Row) -> dict[str, str]:
    """Normaliza una fila a dict, recortando relleno de columnas CHAR y nulos."""
    return {
        "dni": "" if row[0] is None else str(row[0]).strip(),
        "nombre": "" if row[1] is None else str(row[1]).strip(),
        "apellido": "" if row[2] is None else str(row[2]).strip(),
    }


def list_all() -> list[dict[str, str]]:
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(SELECT_ALL_SQL)
        return [_to_dict(row) for row in cursor.fetchall()]


def get_by_dni(dni: str) -> dict[str, str] | None:
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(SELECT_ONE_SQL, dni)
        row = cursor.fetchone()
        return _to_dict(row) if row is not None else None


def create(dni: str, nombre: str, apellido: str) -> None:
    try:
        with get_connection() as connection:
            connection.cursor().execute(INSERT_SQL, dni, nombre, apellido)
    except pyodbc.IntegrityError as exc:
        raise DuplicateKeyError(f"El dni {dni} ya existe.") from exc


def update(dni: str, nombre: str, apellido: str) -> int:
    """Devuelve la cantidad de filas afectadas (0 si el dni no existe)."""
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(UPDATE_SQL, nombre, apellido, dni)
        return cursor.rowcount


def delete(dni: str) -> int:
    """Devuelve la cantidad de filas afectadas (0 si el dni no existe)."""
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(DELETE_SQL, dni)
        return cursor.rowcount
