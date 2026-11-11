# Tarea delegable — Día 1 · Introducción a agentes

> Actividad del tema "Introducción a agentes". Describe una tarea cotidiana del tecnológico que se puede delegar a un agente y cómo se verifica.

## Tarea elegida

Responder la pregunta de un estudiante: **"¿Qué necesito para iniciar mi servicio social?"**

| Entrada | Acciones del agente | Resultado verificable |
|---|---|---|
| Pregunta en lenguaje natural del estudiante. | 1. Valida que la pregunta no esté vacía.<br>2. Busca en `documentos-demo/` las secciones relacionadas con servicio social.<br>3. Selecciona el fragmento con los requisitos.<br>4. Redacta una respuesta breve sin agregar datos.<br>5. Devuelve la respuesta con el documento fuente. | La respuesta lista los requisitos de la sección 3 de `servicio-social.md` y cita ese archivo como fuente. Si la pregunta no está en los documentos, dice que no hay información y recomienda acudir al departamento. |

## Acción que el agente NO debe ejecutar sin autorización

Modificar los documentos de `documentos-demo/` (por ejemplo, para "hacer que una respuesta funcione"), o inventar fechas, montos o requisitos que no aparecen en ellos. Cualquier cambio al corpus lo autoriza una persona.

## Cómo comprobamos que la respuesta es correcta

1. Abrimos `documentos-demo/servicio-social.md`, sección 3, y comparamos punto por punto.
2. Verificamos que la fuente citada existe y que el fragmento mostrado pertenece a ese archivo.
3. Hacemos una pregunta fuera del corpus ("¿Cuál es el horario de la cafetería?") y confirmamos que el agente se abstiene.
4. Esto quedó automatizado en `tests/test_consulta.py` (casos CP-01 y CP-03).
