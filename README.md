# API de Pacientes

CRUD de pacientes sobre **SQL Server** con FastAPI, sin ORM y con SQL parametrizado.
Incluye CORS configurable para el frontend.

## Requisitos

- [uv](https://docs.astral.sh/uv/) (el proyecto fija Python 3.14 en `.python-version`).
- SQL Server accesible y un **ODBC Driver** instalado (`ODBC Driver 18 for SQL Server` por defecto).

## Instalación

```powershell
uv sync
```

## Configuración

1. Copia la plantilla y completa tus credenciales (`.env` está en `.gitignore`):

   ```powershell
   Copy-Item .env.example .env
   ```

2. Variables disponibles:

   | Variable | Obligatoria | Descripción |
   |---|---|---|
   | `DB_DRIVER` | no | Driver ODBC. Por defecto `ODBC Driver 18 for SQL Server`. |
   | `DB_SERVER` | sí | Servidor **sin puerto**: `localhost`, `localhost\SQLEXPRESS`, `192.168.1.10\MIINSTANCIA`. |
   | `DB_NAME` | sí | Base de datos que contiene `dbo.Paciente`. |
   | `DB_TRUSTED_CONNECTION` | no | `yes` usa autenticación de Windows y omite usuario/contraseña. |
   | `DB_USER` / `DB_PASSWORD` | sí* | Credenciales SQL (*salvo con `DB_TRUSTED_CONNECTION=yes`). |
   | `DB_ENCRYPT` / `DB_TRUST_CERT` | no | Por defecto `yes`/`yes` (el Driver 18 cifra y en local suele requerir confiar en el certificado). |
   | `CORS_ORIGINS` | no | Orígenes permitidos, separados por coma. `*` (por defecto) = todos. |
   | `API_HOST` / `API_PORT` | no | Host y puerto de uvicorn. Por defecto `127.0.0.1:8000`. |

   Si algún día necesitas un puerto explícito de SQL Server, escríbelo dentro de `DB_SERVER`
   (por ejemplo `192.168.1.10,1433`); no hay variable de puerto.

## Ejecución

```powershell
uv run uvicorn backend.main:app --reload
```

o con la configuración de `.env`:

```powershell
uv run backend
```

- Documentación interactiva: <http://127.0.0.1:8000/docs>
- Salud: `GET /health`

## Endpoints

| Método | Ruta | Cuerpo | Respuestas |
|---|---|---|---|
| GET | `/pacientes` | — | 200 lista ordenada por apellido y nombre |
| GET | `/pacientes/{dni}` | — | 200 / 404 |
| POST | `/pacientes` | `{"dni","nombre","apellido"}` | 201 / 409 (dni duplicado) / 422 |
| PUT | `/pacientes/{dni}` | `{"nombre","apellido"}` | 200 / 404 / 422 |
| DELETE | `/pacientes/{dni}` | — | 204 / 404 |

Reglas de validación: `dni` debe ser de 8 dígitos (se guarda como texto, conservando ceros),
`nombre` y `apellido` se recortan y aceptan entre 1 y 60 caracteres.

Errores: 404 y 409 devuelven `{"detail": "..."}`; si no hay configuración o la base de datos
falla, la API responde **503** sin filtrar detalles del driver.

### Ejemplo

```powershell
curl.exe -X POST http://127.0.0.1:8000/pacientes -H "Content-Type: application/json" -d '{\"dni\":\"12345678\",\"nombre\":\"Ana\",\"apellido\":\"Pérez\"}'
```

## CORS

`CORSMiddleware` toma los orígenes de `CORS_ORIGINS`:

- `CORS_ORIGINS=*` (por defecto): cualquier origen, `allow_credentials=False` porque el
  estándar CORS prohíbe credenciales con comodín.
- Lista explícita, p. ej. `CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:4200`:
  en ese caso se activan las credenciales (`cookies`, `Authorization`).

Métodos y cabeceras permitidos: todos (`*`), lo que cubre los preflight `OPTIONS` del frontend.

## Tabla esperada

La tabla ya existe; el código asume este esquema en `dbo.Paciente` (ajusta `TABLE` en
`repositories/paciente_repository.py` si tu esquema difiere):

```sql
CREATE TABLE dbo.Paciente (
    dni      VARCHAR(8)  NOT NULL CONSTRAINT PK_Paciente PRIMARY KEY,
    nombre   VARCHAR(60) NULL,
    apellido VARCHAR(60) NULL
);
```

## Estructura

```
src/backend/
  main.py                       # app FastAPI, CORS, handlers de error, arranque
  config.py                     # Settings desde .env (sin puerto de BD)
  database.py                   # get_connection(): commit/rollback/close con pyodbc
  apis/paciente_router.py       # rutas y validación HTTP
  services/paciente_service.py  # reglas de negocio
  services/exceptions.py        # errores de dominio (404 / 409)
  repositories/paciente_repository.py  # SQL parametrizado
  schemas/paciente.py           # PacienteCreate / PacienteUpdate / PacienteOut
```

Dirección de dependencias: `apis` → `services` → `repositories`. Los endpoints son `def`
(no `async`) para que FastAPI los ejecute en el threadpool, ya que `pyodbc` es bloqueante.
