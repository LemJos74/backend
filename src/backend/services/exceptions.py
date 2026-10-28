"""Errores de dominio que la capa API traduce a respuestas HTTP."""


class PacienteNoEncontradoError(LookupError):
    """No existe un paciente con el dni solicitado."""


class PacienteDuplicadoError(ValueError):
    """Ya existe un paciente con ese dni."""
