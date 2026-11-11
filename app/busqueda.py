"""Búsqueda híbrida: palabras clave + ChromaDB (Día 3).

Por qué híbrida: el modelo de embeddings por defecto (all-MiniLM-L6-v2) está entrenado
sobre todo en inglés. En la evaluación con nuestros documentos (ver
documentacion/evidencias/evaluacion-recuperacion.md) encontraba el documento correcto
en el top-3, pero sus distancias no bastaban para decidir si había evidencia: una
pregunta sin respuesta ("¿cuánto cuesta la titulación?") quedaba más cerca (0.38) que
algunas preguntas válidas (0.47).

Reglas (modo ``auto``):
1. Las palabras clave deciden si hay evidencia y de qué documento (abstención del Día 2).
2. Dentro de ese documento, el orden de las secciones combina los dos rankings con
   Reciprocal Rank Fusion (RRF): ChromaDB aporta similitud por significado.
3. Si las palabras clave no encuentran evidencia, ChromaDB solo responde cuando la
   coincidencia es muy fuerte (distancia <= ``TECBOT_UMBRAL``, default 0.30) y comparte
   al menos una palabra con significado con la pregunta.
"""

from __future__ import annotations

from typing import Any

from app import config, rag, vector

RRF_K = 60  # constante estándar de Reciprocal Rank Fusion

# Palabras que aparecen en todo el corpus y no indican relación con el tema.
PALABRAS_GENERICAS = {
    r[:6] for r in ("documento", "documentos", "demostracion", "ejemplo", "corpus", "seccion", "ignora")
}


def _comparte_palabras(pregunta: str, fragmento: dict[str, Any]) -> bool:
    consulta = set(rag.raices(pregunta)) - PALABRAS_GENERICAS
    texto = set(rag.raices(f"{fragmento['tema'].replace('-', ' ')} {fragmento['seccion']} {fragmento['texto']}"))
    return bool(consulta & texto)


def _semantica(pregunta: str, k: int = 8) -> list[dict[str, Any]]:
    """Resultados de ChromaDB agrupados por sección (mejor distancia de cada sección)."""
    vistos: dict[tuple[str, str], dict[str, Any]] = {}
    for r in vector.recuperar(pregunta, limite=k):
        clave = (r["documento"], r["seccion"])
        if clave not in vistos:
            vistos[clave] = r
    return list(vistos.values())


def _fusionar(pregunta: str, limite: int) -> list[dict[str, Any]] | None:
    """Híbrido. None si no hay evidencia suficiente."""
    por_palabras = rag.recuperar_fragmentos(pregunta, limite=limite)
    semanticos = _semantica(pregunta)

    if not por_palabras:
        fuertes = [
            r for r in semanticos
            if r["distancia"] <= config.umbral_distancia() and _comparte_palabras(pregunta, r)
        ]
        if not fuertes:
            return None
        documento = fuertes[0]["documento"]
        return [r for r in fuertes if r["documento"] == documento][:limite]

    documento = por_palabras[0]["documento"]
    ranking_palabras = [r for r in rag.puntuar(pregunta) if r["documento"] == documento]
    ranking_semantico = [r for r in semanticos if r["documento"] == documento]

    puntos: dict[str, float] = {}
    secciones: dict[str, dict[str, Any]] = {}
    for posicion, r in enumerate(ranking_palabras, start=1):
        puntos[r["seccion"]] = puntos.get(r["seccion"], 0.0) + 1 / (RRF_K + posicion)
        secciones[r["seccion"]] = dict(r)
    distancias = {}
    for posicion, r in enumerate(ranking_semantico, start=1):
        puntos[r["seccion"]] = puntos.get(r["seccion"], 0.0) + 1 / (RRF_K + posicion)
        distancias[r["seccion"]] = r["distancia"]
        secciones.setdefault(r["seccion"], dict(r))

    # Solo se citan secciones que las palabras clave consideran relevantes o que ChromaDB
    # ve muy cerca; así no se cuela una sección poco relacionada del mismo documento.
    permitidas = {r["seccion"] for r in por_palabras} | {
        s for s, d in distancias.items() if d <= config.umbral_distancia()
    }
    orden = sorted(permitidas, key=lambda s: puntos.get(s, 0.0), reverse=True)
    salida = []
    for seccion in orden[:limite]:
        fragmento = secciones[seccion]
        fragmento["distancia"] = distancias.get(seccion)
        salida.append(fragmento)
    return salida


def buscar(pregunta: str, limite: int = 3) -> tuple[list[dict[str, Any]], str]:
    """Devuelve (fragmentos, motor usado): ``hibrido``, ``semantica``, ``palabras`` o ``ninguno``."""
    motor = config.motor_busqueda()

    if motor == "palabras" or not vector.disponible():
        if motor == "chroma":
            return [], "ninguno"
        resultados = rag.recuperar_fragmentos(pregunta, limite=limite)
        return (list(resultados), "palabras") if resultados else ([], "ninguno")

    if motor == "chroma":
        fuertes = [
            r for r in _semantica(pregunta)
            if r["distancia"] <= config.umbral_distancia() and _comparte_palabras(pregunta, r)
        ]
        return (fuertes[:limite], "semantica") if fuertes else ([], "ninguno")

    resultados = _fusionar(pregunta, limite)
    return (resultados, "hibrido") if resultados else ([], "ninguno")
