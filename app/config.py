"""Configuración de TecBot Académico (se puede cambiar con variables de entorno)."""

from __future__ import annotations

import os
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CARPETA_DOCUMENTOS = RAIZ / "documentos-demo"
CARPETA_CHROMA = RAIZ / "chroma_db"
COLECCION = "documentos_academicos"


def motor_busqueda() -> str:
    """`auto` (ChromaDB si hay índice, si no palabras clave), `chroma` o `palabras`."""
    return os.getenv("TECBOT_MOTOR", "auto").strip().lower()


def umbral_distancia() -> float:
    """Distancia coseno con la que ChromaDB se considera "muy parecido" (menor = más parecido).

    Calibrado con scripts/evaluar.py: la pregunta sin evidencia más cercana quedó en 0.38,
    así que 0.30 deja margen. Ver documentacion/evidencias/evaluacion-recuperacion.md.
    """
    return float(os.getenv("TECBOT_UMBRAL", "0.30"))


def generador() -> str:
    """`extractivo` (copia el fragmento) u `ollama` (redacta con un modelo local)."""
    return os.getenv("TECBOT_GENERADOR", "extractivo").strip().lower()


def modelo_ollama() -> str:
    return os.getenv("TECBOT_MODELO", "llama3.2:3b")
