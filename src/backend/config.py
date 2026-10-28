"""Configuración de la aplicación, cargada desde el `.env` de la raíz del repo."""

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = REPO_ROOT / ".env"

DEFAULT_DRIVER = "ODBC Driver 18 for SQL Server"


class ConfigurationError(RuntimeError):
    """Falta configuración obligatoria para conectar con SQL Server."""


def _as_bool(value: str | None, default: bool) -> bool:
    if value is None or not value.strip():
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "si", "sí"}


def _as_int(value: str | None, default: int) -> int:
    if value is None or not value.strip():
        return default
    try:
        return int(value.strip())
    except ValueError:
        return default


def _odbc_value(value: str) -> str:
    """Envuelve un valor en llaves para que `;` o espacios no rompan el string ODBC."""
    return "{" + value.replace("}", "}}") + "}"


@dataclass(frozen=True, slots=True)
class Settings:
    db_driver: str
    db_server: str
    db_name: str
    db_user: str
    db_password: str
    db_trusted_connection: bool
    db_encrypt: bool
    db_trust_cert: bool
    cors_origins: tuple[str, ...]
    api_host: str
    api_port: int

    def connection_string(self) -> str:
        """String de conexión ODBC. El servidor va sin puerto: usa el de la instancia."""
        requeridas = [("DB_SERVER", self.db_server), ("DB_NAME", self.db_name)]
        if not self.db_trusted_connection:
            requeridas += [
                ("DB_USER", self.db_user),
                ("DB_PASSWORD", self.db_password),
            ]

        missing = [name for name, value in requeridas if not value]
        if missing:
            raise ConfigurationError(
                "Faltan variables de conexión en el archivo .env: "
                + ", ".join(missing)
                + ". Copia .env.example a .env y complétalo."
            )

        parts = [
            f"DRIVER={_odbc_value(self.db_driver)}",
            f"SERVER={_odbc_value(self.db_server)}",
            f"DATABASE={_odbc_value(self.db_name)}",
        ]
        if self.db_trusted_connection:
            parts.append("Trusted_Connection=yes")
        else:
            parts += [
                f"UID={_odbc_value(self.db_user)}",
                f"PWD={_odbc_value(self.db_password)}",
            ]
        parts += [
            f"Encrypt={'yes' if self.db_encrypt else 'no'}",
            f"TrustServerCertificate={'yes' if self.db_trust_cert else 'no'}",
        ]
        return ";".join(parts) + ";"


@lru_cache
def get_settings() -> Settings:
    load_dotenv(ENV_FILE, override=False)

    origins = tuple(
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "*").split(",")
        if origin.strip()
    )

    return Settings(
        db_driver=os.getenv("DB_DRIVER", "").strip() or DEFAULT_DRIVER,
        db_server=os.getenv("DB_SERVER", "").strip(),
        db_name=os.getenv("DB_NAME", "").strip(),
        db_user=os.getenv("DB_USER", "").strip(),
        db_password=os.getenv("DB_PASSWORD", ""),
        db_trusted_connection=_as_bool(
            os.getenv("DB_TRUSTED_CONNECTION"), default=False
        ),
        db_encrypt=_as_bool(os.getenv("DB_ENCRYPT"), default=True),
        db_trust_cert=_as_bool(os.getenv("DB_TRUST_CERT"), default=True),
        cors_origins=origins or ("*",),
        api_host=os.getenv("API_HOST", "").strip() or "127.0.0.1",
        api_port=_as_int(os.getenv("API_PORT"), default=8000),
    )
