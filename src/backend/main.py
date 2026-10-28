"""Punto de entrada de la API: app FastAPI, CORS y traducción de errores a HTTP."""

import logging

import pyodbc
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.apis.paciente_router import router as paciente_router
from backend.config import ConfigurationError, get_settings
from backend.services.exceptions import (
    PacienteDuplicadoError,
    PacienteNoEncontradoError,
)

logger = logging.getLogger("backend")

DESCRIPTION = """
API para gestionar pacientes (dni, nombre, apellido) sobre SQL Server.
"""


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="API de Pacientes",
        description=DESCRIPTION,
        version="0.1.0",
    )

    # Con orígenes "*" el estándar CORS no permite credenciales (cookies).
    permite_credenciales = "*" not in settings.cors_origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_origins),
        allow_credentials=permite_credenciales,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(paciente_router)

    @app.get("/health", tags=["Salud"], summary="Comprobación de vida")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.exception_handler(PacienteNoEncontradoError)
    def _no_encontrado(request: Request, exc: PacienteNoEncontradoError) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(PacienteDuplicadoError)
    def _duplicado(request: Request, exc: PacienteDuplicadoError) -> JSONResponse:
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    @app.exception_handler(ConfigurationError)
    def _sin_configuracion(request: Request, exc: ConfigurationError) -> JSONResponse:
        logger.error("Configuración incompleta: %s", exc)
        return JSONResponse(status_code=503, content={"detail": str(exc)})

    @app.exception_handler(pyodbc.Error)
    def _error_bd(request: Request, exc: pyodbc.Error) -> JSONResponse:
        # No se expone el detalle del driver al cliente.
        logger.error("Error de base de datos en %s: %s", request.url.path, exc)
        return JSONResponse(
            status_code=503,
            content={
                "detail": "No se pudo completar la operación contra la base de datos."
            },
        )

    return app


app = create_app()


def run() -> None:
    """Levanta el servidor con la configuración de `API_HOST` / `API_PORT`."""
    import uvicorn

    settings = get_settings()
    uvicorn.run("backend.main:app", host=settings.api_host, port=settings.api_port)
