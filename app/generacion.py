"""Redacción de la respuesta (Día 2: extractiva, sin modelo de lenguaje).

Se arma la respuesta con el texto del fragmento mejor clasificado, sin agregar
información. En el Día 3 esta función podrá llamar a un modelo (Ollama u otro
proveedor) manteniendo la misma firma.
"""

from __future__ import annotations

import re

from app.rag import Resultado

LONGITUD_MAXIMA_RESPUESTA = 700
LONGITUD_MAXIMA_FRAGMENTO = 300

RESPUESTA_SIN_EVIDENCIA = "No encontré información suficiente en los documentos disponibles."
ADVERTENCIA_SIN_EVIDENCIA = (
    "Acude al departamento correspondiente para confirmar esta información."
)


def limpiar_markdown(texto: str) -> str:
    """Quita marcas de Markdown que no se leen bien como texto plano."""
    lineas: list[str] = []
    for linea in texto.splitlines():
        linea = linea.strip()
        if not linea or set(linea) <= set("|-: "):
            continue  # líneas vacías y separadores de tabla
        if linea.startswith("|"):
            celdas = [c.strip() for c in linea.strip("|").split("|") if c.strip()]
            linea = "- " + " · ".join(celdas)
        linea = re.sub(r"^>\s?", "", linea)
        linea = linea.replace("**", "").replace("`", "")
        lineas.append(linea)
    return "\n".join(lineas)


def recortar(texto: str, limite: int) -> str:
    """Recorta en el último salto de línea o espacio antes del límite."""
    if len(texto) <= limite:
        return texto
    corte = texto.rfind("\n", 0, limite)
    if corte < limite // 2:
        corte = texto.rfind(" ", 0, limite)
    return texto[:corte].rstrip() + " …"


def resumir_fragmento(fragmento: Resultado) -> str:
    return recortar(limpiar_markdown(fragmento["texto"]), LONGITUD_MAXIMA_FRAGMENTO)


def generar_respuesta(pregunta: str, fragmentos: list[Resultado]) -> str:
    """Construye una respuesta breve citando el fragmento principal."""
    if not fragmentos:
        return RESPUESTA_SIN_EVIDENCIA
    principal = fragmentos[0]
    cuerpo = recortar(limpiar_markdown(principal["texto"]), LONGITUD_MAXIMA_RESPUESTA)
    return f"Según «{principal['seccion']}» ({principal['documento']}):\n{cuerpo}"
