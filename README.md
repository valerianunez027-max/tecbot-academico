# TecBot Académico

Asistente de información académica desarrollado en el curso-taller
"Creación de software con Agentes de IA" (Congreso Ciencias Revueltas 2026, ITS Santiago Papasquiaro).

Responde preguntas sobre servicio social, residencias, titulación y acreditación
citando la fuente, y avisa cuando no tiene información.

> **Prototipo académico.** Los documentos de `documentos-demo/` son ficticios y no son normativa oficial.

## Requisitos

- Python 3.11+
- Git
- OpenCode (para trabajar con los agentes)

## Ejecución local (Windows / PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts\indexar.py
uvicorn app.main:app --reload
```

`indexar.py` crea la base vectorial `chroma_db/` (Día 3). Sin ese paso, TecBot funciona igual con búsqueda por palabras clave.

Abre http://localhost:8000 para usar la interfaz, o http://localhost:8000/docs para probar la API.

Si PowerShell no deja activar el entorno, ejecuta una vez:
`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

## Pruebas

```powershell
pytest -q
```

## Búsqueda (RAG) y configuración

| Variable | Valores | Default |
|---|---|---|
| `TECBOT_MOTOR` | `auto` (híbrido: palabras clave + ChromaDB), `chroma`, `palabras` | `auto` |
| `TECBOT_UMBRAL` | distancia con la que ChromaDB responde sin palabras clave | `0.30` |
| `TECBOT_GENERADOR` | `extractivo`, `ollama` | `extractivo` |
| `TECBOT_MODELO` | modelo de Ollama | `llama3.2:3b` |

Ejemplo en PowerShell: `$env:TECBOT_GENERADOR = "ollama"` y luego `uvicorn app.main:app --reload`.

Herramientas: `python scripts\consultar.py "tu pregunta"` muestra los fragmentos y distancias; `python scripts\evaluar.py` genera la tabla de evaluación.

## API

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/salud` | Estado del servicio |
| POST | `/api/consulta` | `{"pregunta": "..."}` → `respuesta`, `fuentes`, `advertencia` |

Detalle en [`documentacion/arquitectura.md`](documentacion/arquitectura.md).

## Trabajo con agentes (OpenCode)

Los agentes están en `.opencode/agents/`: `coordinador` (primario) y los subagentes
`@arquitecto`, `@disenador-web`, `@desarrollador` y `@tester`. Reglas y contexto en [`AGENTS.md`](AGENTS.md).

## Estado

- Día 1: requerimientos, AGENTS.md, landing page y repositorio.
- Día 2: API de consulta con búsqueda por palabra clave, subagentes y pruebas.
- Día 3: recuperación semántica con ChromaDB, generación opcional con Ollama. Pendiente: MCP.
