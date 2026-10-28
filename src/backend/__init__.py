def main() -> None:
    """Punto de entrada del CLI `backend`: arranca el servidor uvicorn."""
    from backend.main import run

    run()
