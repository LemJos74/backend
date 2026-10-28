"""Conexión a SQL Server con pyodbc (sin ORM)."""

from collections.abc import Iterator
from contextlib import contextmanager

import pyodbc

from backend.config import get_settings

CONNECT_TIMEOUT_SECONDS = 10


@contextmanager
def get_connection() -> Iterator[pyodbc.Connection]:
    """Abre una conexión, confirma si todo va bien y la cierra siempre."""
    settings = get_settings()
    connection = pyodbc.connect(
        settings.connection_string(),
        autocommit=False,
        timeout=CONNECT_TIMEOUT_SECONDS,
    )
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
