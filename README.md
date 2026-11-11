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
uvicorn app.main:app --reload
```

Abre http://localhost:8000 para usar la interfaz, o http://localhost:8000/docs para probar la API.

Si PowerShell no deja activar el entorno, ejecuta una vez:
`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

## Pruebas

```powershell
pytest -q
```

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
- Día 3 (pendiente): recuperación semántica con ChromaDB y MCP.
