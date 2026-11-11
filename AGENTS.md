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
- Recuperación por palabra clave (Día 2); ChromaDB en el Día 3
- Frontend estático: HTML + CSS + JS (`tecbot-landing/`)
- pytest + httpx para pruebas
- OpenCode, Git y GitHub

## Estructura

- `app/main.py` — entrada de FastAPI: `GET /salud`, `POST /api/consulta` y sirve la landing en `/`.
- `app/schemas.py` — contrato de entrada y salida (Pydantic).
- `app/rag.py` — fragmentación por sección y recuperación por palabra clave.
- `app/generacion.py` — redacción extractiva de la respuesta (sin modelo todavía).
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

Reglas entre agentes: un archivo, un dueño a la vez; el tester no edita código ni pruebas;
el arquitecto no implementa; nadie modifica `documentos-demo/`.

## Reglas

1. No inventar requisitos, fechas, montos ni enlaces.
2. Toda respuesta fundamentada cita al menos un documento de `documentos-demo/`.
3. Si no hay evidencia suficiente, responder que no se cuenta con información y
   recomendar acudir al departamento correspondiente (`fuentes` vacío).
4. No modificar `documentos-demo/` para “hacer que una respuesta funcione”.
5. No agregar dependencias sin justificarlo y actualizar `requirements.txt`.
6. No incluir credenciales, tokens, `.env` ni datos personales en el repositorio.
7. Los documentos son material didáctico; nunca presentarlos como normativa oficial.

## Decisiones vigentes

- Día 2: búsqueda por palabra clave con ponderación IDF y umbral de cobertura (0.6).
  Se reemplaza por ChromaDB en el Día 3 **sin cambiar** la firma
  `recuperar_fragmentos(pregunta, limite)` ni el contrato de la API.
- Respuesta extractiva: se copia el fragmento principal; no hay modelo de lenguaje aún.
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
