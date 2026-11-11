"""Recuperación semántica con ChromaDB (Día 3).

El índice se construye con ``python scripts/indexar.py`` y vive en ``chroma_db/``.
Si ChromaDB no está instalado o el índice no existe, ``disponible()`` devuelve False
y la API sigue funcionando con la búsqueda por palabras clave de ``app/rag.py``.
"""

from __future__ import annotations

import re
from functools import lru_cache
from typing import Any

from app import config
from app.rag import cargar_fragmentos

TAMANO_FRAGMENTO = 800
SOLAPAMIENTO = 120


# ---------------------------------------------------------------- fragmentación
def dividir_texto(texto: str, tamano: int = TAMANO_FRAGMENTO, solapamiento: int = SOLAPAMIENTO) -> list[str]:
    """Agrupa párrafos hasta ``tamano`` caracteres, conservando un poco de contexto."""
    parrafos = [p.strip() for p in re.split(r"\n\s*\n", texto) if p.strip()]
    fragmentos: list[str] = []
    actual = ""
    for parrafo in parrafos:
        if len(actual) + len(parrafo) + 2 <= tamano:
            actual = f"{actual}\n\n{parrafo}".strip()
            continue
        if actual:
            fragmentos.append(actual)
            actual = f"{actual[-solapamiento:]}\n\n{parrafo}".strip()
        else:
            fragmentos.append(parrafo)
            actual = ""
    if actual:
        fragmentos.append(actual)
    return fragmentos


def preparar_fragmentos() -> tuple[list[str], list[str], list[dict[str, Any]]]:
    """Ids, textos y metadatos listos para ``upsert``.

    Se parte de las secciones (``## ``) de cada documento y se subdividen las largas.
    El texto indexado lleva el encabezado de la sección para mejorar la búsqueda.
    """
    ids: list[str] = []
    textos: list[str] = []
    metadatos: list[dict[str, Any]] = []
    contador: dict[str, int] = {}
    for seccion in cargar_fragmentos(config.CARPETA_DOCUMENTOS):
        for parte in dividir_texto(seccion["texto"]):
            indice = contador.get(seccion["tema"], 0)
            contador[seccion["tema"]] = indice + 1
            ids.append(f"{seccion['tema']}-{indice:03d}")
            textos.append(f"{seccion['seccion']}\n\n{parte}")
            metadatos.append(
                {
                    "documento": seccion["documento"],
                    "tema": seccion["tema"],
                    "seccion": seccion["seccion"],
                    "fragmento": indice,
                    "tipo": "demostracion",
                }
            )
    return ids, textos, metadatos


# ---------------------------------------------------------------- cliente
def _cliente():
    import chromadb
    from chromadb.config import Settings

    return chromadb.PersistentClient(
        path=str(config.CARPETA_CHROMA), settings=Settings(anonymized_telemetry=False)
    )


def _funcion_embeddings():
    from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

    return DefaultEmbeddingFunction()


@lru_cache(maxsize=1)
def _coleccion():
    """Colección abierta una sola vez por proceso; None si no se puede usar."""
    if not config.CARPETA_CHROMA.is_dir():
        return None
    try:
        coleccion = _cliente().get_collection(
            name=config.COLECCION, embedding_function=_funcion_embeddings()
        )
        return coleccion if coleccion.count() > 0 else None
    except Exception:  # noqa: BLE001 - sin chromadb o sin colección: se usa el respaldo
        return None


def disponible() -> bool:
    return _coleccion() is not None


def reiniciar_cache() -> None:
    """Olvida la colección abierta (útil después de reindexar)."""
    _coleccion.cache_clear()


def construir_indice() -> int:
    """Borra y vuelve a crear la colección con todos los documentos. Devuelve el total."""
    cliente = _cliente()
    try:
        cliente.delete_collection(config.COLECCION)
    except Exception:  # noqa: BLE001 - no existía todavía
        pass
    coleccion = cliente.create_collection(
        name=config.COLECCION,
        embedding_function=_funcion_embeddings(),
        metadata={"hnsw:space": "cosine"},
    )
    ids, textos, metadatos = preparar_fragmentos()
    if not ids:
        raise RuntimeError("No se encontraron documentos para indexar.")
    coleccion.upsert(ids=ids, documents=textos, metadatas=metadatos)
    reiniciar_cache()
    return coleccion.count()


# ---------------------------------------------------------------- consulta
def recuperar(pregunta: str, limite: int = 4) -> list[dict[str, Any]]:
    """Fragmentos más parecidos a la pregunta, del más al menos cercano (sin filtrar)."""
    coleccion = _coleccion()
    if coleccion is None:
        return []
    resultados = coleccion.query(
        query_texts=[pregunta],
        n_results=limite,
        include=["documents", "metadatas", "distances"],
    )
    salida: list[dict[str, Any]] = []
    for texto, meta, distancia in zip(
        resultados["documents"][0], resultados["metadatas"][0], resultados["distances"][0]
    ):
        seccion = str(meta.get("seccion", ""))
        cuerpo = texto[len(seccion):].lstrip() if seccion and texto.startswith(seccion) else texto
        salida.append(
            {
                "documento": meta["documento"],
                "tema": meta["tema"],
                "seccion": seccion,
                "texto": cuerpo,
                "distancia": round(float(distancia), 4),
                "puntaje": round(1 - float(distancia), 4),
                "cobertura": round(1 - float(distancia), 4),
            }
        )
    return salida
