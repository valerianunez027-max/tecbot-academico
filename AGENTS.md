# AGENTS.md — TecBot Académico

## Propósito

Asistente de información académica para estudiantes del ITS Santiago Papasquiaro.
Responde preguntas sobre servicio social, residencias, titulación y acreditación
usando únicamente los documentos de `documentos-demo/`.

## Alcance

Incluye:
- Consultas en lenguaje natural.
- Recuperación de fragmentos documentales.
- Respuestas con fuentes.
- Derivación al departamento cuando no hay evidencia.

No incluye:
- Autenticación de usuarios.
- Trámites oficiales ni firmas.
- Datos personales.
- Normativa institucional real.

## Stack

- Python 3.11+ con FastAPI + Uvicorn + Pydantic
- ChromaDB (embeddings `all-MiniLM-L6-v2`) con respaldo por palabras clave
- Ollama (`llama3.2:3b`) opcional para redactar respuestas
- Frontend estático: HTML + CSS + JS (`tecbot-landing/`)
- pytest + httpx para pruebas
- OpenCode, Git y GitHub

## Estructura

- `app/main.py` — entrada de FastAPI: `GET /salud`, `POST /api/consulta` y sirve la landing en `/`.
- `app/schemas.py` — contrato de entrada y salida (Pydantic).
- `app/config.py` — rutas y variables de entorno (`TECBOT_MOTOR`, `TECBOT_UMBRAL`, `TECBOT_GENERADOR`).
- `app/rag.py` — fragmentación por sección y recuperación por palabra clave (respaldo).
- `app/vector.py` — índice y consulta en ChromaDB (`chroma_db/`, no se versiona).
- `app/busqueda.py` — búsqueda híbrida: palabras clave deciden la evidencia; ChromaDB ordena (RRF).
- `app/generacion.py` — respuesta extractiva u Ollama con prompt anclado a los fragmentos.
- `scripts/` — `indexar.py`, `consultar.py`, `evaluar.py`, `verificar_entorno.py` y `mcp_documentos.py` (servidor MCP de solo lectura).
- `tecbot-landing/` — interfaz: `index.html`, `styles.css`, `app.js`, `assets/logo.svg`.
- `documentos-demo/` — corpus ficticio de demostración (solo lectura).
- `documentacion/` — arquitectura, diseño, pruebas y evidencias.
- `requerimientos.md` — RF, RNF e historias de usuario.
- `.opencode/agents/` — coordinador y subagentes (prompt + permisos en el frontmatter).
- `tests/` — pruebas automatizadas.

## Comandos (Windows / PowerShell, desde la raíz)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts\indexar.py         # crea chroma_db/ (repetir si cambian los documentos)
python scripts\evaluar.py         # tabla de distancias en documentacion/evidencias/
uvicorn app.main:app --reload     # abre http://localhost:8000
pytest -q
```

## Equipo de agentes

| Agente | Tipo | Responsabilidad | Puede editar |
|---|---|---|---|
| `coordinador` | primario | Descompone, delega, revisa e integra | Con plan aprobado |
| `@arquitecto` | subagente | Estructura, contratos de API, riesgos | No |
| `@disenador-web` | subagente | Sistema de diseño e interfaz | Solo `tecbot-landing/` y `documentacion/design.md` |
| `@desarrollador` | subagente | Implementa endpoints, lógica y pruebas | `app/`, `tests/` (bash con permiso) |
| `@tester` | subagente | Ejecuta pruebas y reporta defectos | No (solo pytest y git de lectura) |

MCP: el servidor `documentos_academicos` solo lee `documentos-demo/` (ver `opencode.json`).

Reglas entre agentes: un archivo, un dueño a la vez; el tester no edita código ni pruebas;
el arquitecto no implementa; nadie modifica `documentos-demo/`.

## Reglas

1. No inventar requisitos, fechas, montos ni enlaces.
2. Toda respuesta fundamentada cita al menos un documento de `documentos-demo/`.
3. Si no hay evidencia suficiente, responder que no se cuenta con información y
   recomendar acudir al departamento correspondiente (`fuentes` vacío).
4. No modificar `documentos-demo/` para “hacer que una respuesta funcione”.
5. No agregar dependencias sin justificarlo y actualizar `requirements.txt`.
   Tras cambiar `documentos-demo/` o la fragmentación, reindexar con `scripts/indexar.py`.
6. No incluir credenciales, tokens, `.env` ni datos personales en el repositorio.
7. Los documentos son material didáctico; nunca presentarlos como normativa oficial.

## Decisiones vigentes

- Día 3: búsqueda **híbrida**. Las palabras clave deciden si hay evidencia y el documento;
  ChromaDB reordena las secciones con Reciprocal Rank Fusion. ChromaDB responde solo si la
  distancia es <= `TECBOT_UMBRAL` (0.30). Motivo: con ChromaDB solo la evaluación dio 7/9
  (embeddings en inglés; una pregunta sin respuesta quedó a 0.38 y una válida a 0.47).
  El contrato de la API **no cambió** (solo se agregó `distancia` opcional en cada fuente).
- Respuesta extractiva por defecto; `TECBOT_GENERADOR=ollama` redacta con `llama3.2:3b`.
- Las pruebas de contrato usan `TECBOT_MOTOR=palabras` (deterministas); ChromaDB se prueba en `tests/test_vector.py`.
- Las fuentes de una respuesta provienen de un solo documento para no mezclar temas.

## Convenciones

- Python con type hints en funciones públicas.
- Nombres de archivos en snake_case; documentos del corpus en kebab-case.
- Rutas de API en español.
- Respuestas JSON con las claves `respuesta`, `fuentes` y `advertencia`.
- Mensajes de commit en formato Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`, `chore:`).

## Definición de terminado

Una tarea está terminada cuando:
- Las pruebas pasan (`pytest -q`) y se muestra la salida real.
- Existe al menos una prueba para el caso feliz y una para el caso sin evidencia.
- Se actualizó la documentación afectada (incluido este archivo si cambió la arquitectura).
- El cambio fue revisado con `git diff`.
