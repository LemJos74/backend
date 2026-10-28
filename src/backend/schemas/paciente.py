"""Esquemas del recurso Paciente."""

from pydantic import BaseModel, ConfigDict, Field, field_validator

DNI_PATTERN = r"^\d{8}$"
# Coincide con las columnas VARCHAR(60) de la tabla dbo.Paciente.
MAX_NAME_LENGTH = 60


def _sin_espacios_sobrantes(value: object) -> object:
    return value.strip() if isinstance(value, str) else value


class PacienteCreate(BaseModel):
    """Cuerpo de `POST /pacientes`."""

    dni: str = Field(
        pattern=DNI_PATTERN,
        examples=["12345678"],
        description="DNI de 8 dígitos (se conserva como texto).",
    )
    nombre: str = Field(min_length=1, max_length=MAX_NAME_LENGTH, examples=["Ana"])
    apellido: str = Field(min_length=1, max_length=MAX_NAME_LENGTH, examples=["Pérez"])

    _limpiar = field_validator("dni", "nombre", "apellido", mode="before")(
        _sin_espacios_sobrantes
    )


class PacienteUpdate(BaseModel):
    """Cuerpo de `PUT /pacientes/{dni}`: el dni es la clave y no se modifica."""

    nombre: str = Field(min_length=1, max_length=MAX_NAME_LENGTH, examples=["Ana"])
    apellido: str = Field(min_length=1, max_length=MAX_NAME_LENGTH, examples=["Pérez"])

    _limpiar = field_validator("nombre", "apellido", mode="before")(
        _sin_espacios_sobrantes
    )


class PacienteOut(BaseModel):
    """Representación devuelta por la API.

    No reutiliza las validaciones de entrada: así una fila antigua con nombres
    vacíos o nulos en la base de datos no rompe la respuesta.
    """

    model_config = ConfigDict(from_attributes=True)

    dni: str
    nombre: str
    apellido: str
