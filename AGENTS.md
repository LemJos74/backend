# AGENTS.md

## Project state

FastAPI CRUD for `dbo.Paciente` (dni / nombre / apellido) over SQL Server, already implemented with the required layers: `main.py` → `apis` → `services` → `repositories`, plus `schemas`, `config.py` (`.env`) and `database.py` (`pyodbc` connection helper). CORS is configured from `CORS_ORIGINS`. See `README.md` for endpoints and env vars.

## Toolchain

- Use `uv` for everything; do not invoke `python`, `pip`, or `pytest` directly.
- Python is pinned to 3.14 via `.python-version` (`requires-python = ">=3.14"`); `uv` will fetch it if missing.
- `uv sync` installs the project in editable mode; `uv run <cmd>` runs inside the project venv.
- Add dependencies with `uv add <pkg>` (or `uv add --dev <pkg>`); this updates both `pyproject.toml` and `uv.lock` — commit both.
- On Windows, `uv` may warn about hardlink fallback; harmless, optionally set `UV_LINK_MODE=copy`.

## Layout and entrypoint

- src layout: the import package is `backend` at `src/backend/` (uv_build's default). Put new modules there, not at the repo root.
- Required layered structure, in call order: `main.py` → `apis` → `services` → `repositories`, plus `schemas` for request/response and data models. Create these as modules/packages under `src/backend/`.
- Respect the layer direction: `apis` must not access `repositories` directly, and `repositories` must not contain business logic or HTTP concerns. Keep SQL in `repositories`, business rules in `services`, and routing/validation wiring in `apis`.
- CLI entrypoint is declared as `backend = "backend:main"` in `pyproject.toml`; run it with `uv run backend`.
- When adding a FastAPI app, expose it from `src/backend/main.py` and document the exact `uv run uvicorn ...` command here or in the README.

## Database

- Target database is **SQL Server**.
- **Do not use an ORM** (no SQLAlchemy ORM, Django ORM, Peewee, etc.). Use the SQL Server driver directly with hand-written SQL/parameterized queries in `repositories`.
- Connection settings come from a `.env` file at the repo root. Load it explicitly (no settings framework is set up yet); never hardcode credentials.
- `.env` is in `.gitignore`; commit `.env.example` as the template instead.
- Installed and used: `pyodbc` (no ORM), `python-dotenv`, `uvicorn`. Settings live in `src/backend/config.py`; the connection helper is `src/backend/database.py`. `DB_SERVER` carries no port (use `host\instance` or `host,port` when needed) and `DB_TRUSTED_CONNECTION=yes` switches to Windows auth.

## Verification

No tests, linter, formatter, or type checker are configured. Do not assume pytest/ruff/mypy exist. At minimum verify changes with `uv run python -c "import backend"`, `uv run python -c "from backend.main import app"` and `uv run uvicorn backend.main:app`; add dev tooling via `uv add --dev` if the task calls for it.
