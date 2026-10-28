"""Reglas de negocio del recurso Paciente."""

from backend.repositories import paciente_repository
from backend.repositories.paciente_repository import DuplicateKeyError
from backend.schemas.paciente import PacienteCreate, PacienteUpdate
from backend.services.exceptions import (
    PacienteDuplicadoError,
    PacienteNoEncontradoError,
)

Paciente = dict[str, str]


def listar() -> list[Paciente]:
    return paciente_repository.list_all()


def obtener(dni: str) -> Paciente:
    paciente = paciente_repository.get_by_dni(dni)
    if paciente is None:
        raise PacienteNoEncontradoError(f"No existe un paciente con dni {dni}.")
    return paciente


def crear(payload: PacienteCreate) -> Paciente:
    dni = payload.dni
    if paciente_repository.get_by_dni(dni) is not None:
        raise PacienteDuplicadoError(f"Ya existe un paciente con dni {dni}.")

    try:
        paciente_repository.create(dni, payload.nombre, payload.apellido)
    except DuplicateKeyError as exc:
        # Otra petición insertó el mismo dni entre la comprobación y el INSERT.
        raise PacienteDuplicadoError(f"Ya existe un paciente con dni {dni}.") from exc

    return {"dni": dni, "nombre": payload.nombre, "apellido": payload.apellido}


def actualizar(dni: str, payload: PacienteUpdate) -> Paciente:
    if paciente_repository.update(dni, payload.nombre, payload.apellido) == 0:
        raise PacienteNoEncontradoError(f"No existe un paciente con dni {dni}.")
    return {"dni": dni, "nombre": payload.nombre, "apellido": payload.apellido}


def eliminar(dni: str) -> None:
    if paciente_repository.delete(dni) == 0:
        raise PacienteNoEncontradoError(f"No existe un paciente con dni {dni}.")
