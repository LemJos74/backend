"""Rutas HTTP del recurso Paciente (solo cablean service + validación)."""

from typing import Annotated

from fastapi import APIRouter, Path, status

from backend.schemas.paciente import DNI_PATTERN, PacienteCreate, PacienteOut, PacienteUpdate
from backend.services import paciente_service

router = APIRouter(prefix="/pacientes", tags=["Pacientes"])

DniPath = Annotated[
    str,
    Path(pattern=DNI_PATTERN, description="DNI de 8 dígitos", examples=["12345678"]),
]


@router.get(
    "",
    response_model=list[PacienteOut],
    summary="Listar pacientes",
    description="Devuelve todos los pacientes ordenados por apellido y nombre.",
)
def listar_pacientes() -> list[dict[str, str]]:
    return paciente_service.listar()


@router.get(
    "/{dni}",
    response_model=PacienteOut,
    summary="Obtener un paciente",
    responses={404: {"description": "El dni no existe"}},
)
def obtener_paciente(dni: DniPath) -> dict[str, str]:
    return paciente_service.obtener(dni)


@router.post(
    "",
    response_model=PacienteOut,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un paciente",
    responses={409: {"description": "Ya existe un paciente con ese dni"}},
)
def crear_paciente(payload: PacienteCreate) -> dict[str, str]:
    return paciente_service.crear(payload)


@router.put(
    "/{dni}",
    response_model=PacienteOut,
    summary="Actualizar un paciente",
    description="Reemplaza nombre y apellido. El dni no se modifica.",
    responses={404: {"description": "El dni no existe"}},
)
def actualizar_paciente(dni: DniPath, payload: PacienteUpdate) -> dict[str, str]:
    return paciente_service.actualizar(dni, payload)


@router.delete(
    "/{dni}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un paciente",
    responses={404: {"description": "El dni no existe"}},
)
def eliminar_paciente(dni: DniPath) -> None:
    paciente_service.eliminar(dni)
