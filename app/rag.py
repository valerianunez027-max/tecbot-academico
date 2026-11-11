"""Recuperación documental por palabra clave (Día 2).

Divide los documentos de ``documentos-demo/`` en fragmentos por sección (``## ``)
y los ordena según las palabras de la pregunta, ponderadas por qué tan raras son
en el corpus (IDF). En el Día 3 se reemplazará por búsqueda semántica con ChromaDB
sin cambiar la firma de ``recuperar_fragmentos``.
"""

from __future__ import annotations

import math
import re
import unicodedata
from functools import lru_cache
from pathlib import Path
from typing import TypedDict

CARPETA_DOCUMENTOS = Path(__file__).resolve().parent.parent / "documentos-demo"

# Fracción mínima de la pregunta (ponderada por IDF) que debe encontrarse en el
# mejor fragmento para considerar que hay evidencia suficiente.
UMBRAL_COBERTURA = 0.6

# Longitud del prefijo usado como raíz ("acreditar" y "acreditación" -> "acredi").
LONGITUD_RAIZ = 6

PALABRAS_VACIAS = {
    "que", "como", "cual", "cuales", "cuando", "donde", "quien", "para", "por",
    "con", "sin", "una", "uno", "unos", "unas", "las", "los", "del", "este",
    "esta", "estos", "estas", "ese", "esa", "son", "hay", "tengo", "tiene",
    "puedo", "puede", "debo", "debe", "quiero", "saber",
    "hacer", "hago", "sobre", "entre", "pero", "mas", "muy", "todo", "toda",
    "todos", "mis", "tus", "sus", "nos", "les", "algo", "cuanto", "cuantos",
}

# Formas de preguntar por requisitos que no aparecen literalmente en los documentos.
SINONIMOS = {"necesito": "requisitos", "necesita": "requisitos", "requiero": "requisitos", "piden": "requisitos"}


# Secciones que describen al documento de demostración y no al trámite.
SECCIONES_EXCLUIDAS = ("proposito", "alcance", "fuente y vigencia", "limites")


class Fragmento(TypedDict):
    documento: str
    tema: str
    seccion: str
    texto: str


class Resultado(TypedDict):
    documento: str
    tema: str
    seccion: str
    texto: str
    puntaje: float
    cobertura: float


def normalizar(texto: str) -> str:
    """Minúsculas y sin acentos."""
    sin_acentos = unicodedata.normalize("NFD", texto.lower())
    return "".join(c for c in sin_acentos if unicodedata.category(c) != "Mn")


def raices(texto: str) -> list[str]:
    """Raíces de las palabras significativas de un texto."""
    palabras = [SINONIMOS.get(p, p) for p in re.findall(r"[a-z0-9]+", normalizar(texto))]
    return [p[:LONGITUD_RAIZ] for p in palabras if len(p) >= 4 and p not in PALABRAS_VACIAS]


def _dividir_en_secciones(nombre: str, contenido: str) -> list[Fragmento]:
    tema = Path(nombre).stem
    titulo = contenido.splitlines()[0].lstrip("# ").split("—")[0].strip() if contenido else tema
    fragmentos: list[Fragmento] = []
    for bloque in re.split(r"^## ", contenido, flags=re.MULTILINE)[1:]:
        encabezado, _, cuerpo = bloque.partition("\n")
        seccion = re.sub(r"^\d+\.\s*", "", encabezado).strip()
        cuerpo = cuerpo.strip()
        if normalizar(seccion).startswith(SECCIONES_EXCLUIDAS):
            continue
        if cuerpo:
            fragmentos.append(
                Fragmento(documento=nombre, tema=tema, seccion=f"{titulo} · {seccion}", texto=cuerpo)
            )
    return fragmentos


@lru_cache(maxsize=1)
def cargar_fragmentos(carpeta: Path = CARPETA_DOCUMENTOS) -> tuple[Fragmento, ...]:
    """Lee y fragmenta todos los ``.md`` de la carpeta del corpus."""
    fragmentos: list[Fragmento] = []
    for ruta in sorted(carpeta.glob("*.md")):
        fragmentos.extend(_dividir_en_secciones(ruta.name, ruta.read_text(encoding="utf-8")))
    return tuple(fragmentos)


@lru_cache(maxsize=1)
def _indice(carpeta: Path = CARPETA_DOCUMENTOS) -> tuple[list[set[str]], dict[str, float], float]:
    fragmentos = cargar_fragmentos(carpeta)
    conjuntos = [
        set(raices(f"{f['tema'].replace('-', ' ')} {f['seccion']} {f['texto']}")) for f in fragmentos
    ]
    total = len(conjuntos)
    frecuencia: dict[str, int] = {}
    for conjunto in conjuntos:
        for raiz in conjunto:
            frecuencia[raiz] = frecuencia.get(raiz, 0) + 1
    idf = {raiz: math.log((total + 1) / (n + 1)) + 1 for raiz, n in frecuencia.items()}
    idf_desconocida = math.log(total + 1) + 1  # palabra que no aparece en el corpus
    return conjuntos, idf, idf_desconocida


def puntuar(pregunta: str) -> list[Resultado]:
    """Todos los fragmentos con al menos una coincidencia, del mejor al peor (sin filtrar)."""
    consulta = set(raices(pregunta))
    if not consulta:
        return []

    fragmentos = cargar_fragmentos()
    conjuntos, idf, idf_desconocida = _indice()
    peso_total = sum(idf.get(r, idf_desconocida) for r in consulta)

    resultados: list[Resultado] = []
    for fragmento, conjunto in zip(fragmentos, conjuntos):
        coincidencias = consulta & conjunto
        if not coincidencias:
            continue
        relevancia = sum(idf[r] for r in coincidencias)
        # Desempate: palabras en el encabezado de la sección y frecuencia en el texto.
        encabezado = set(raices(fragmento["seccion"].split("·")[-1]))
        bono_encabezado = 0.5 * sum(idf[r] for r in coincidencias & encabezado)
        # Bono si la pregunta nombra el tema del documento (p. ej. "servicio social").
        bono_tema = 2.0 if consulta & set(raices(fragmento["tema"].replace("-", " "))) else 0.0
        frecuencia = sum(1 for r in raices(fragmento["texto"]) if r in consulta)
        puntaje = relevancia + bono_encabezado + bono_tema + 0.1 * math.log1p(frecuencia)
        resultados.append(
            Resultado(**fragmento, puntaje=round(puntaje, 3), cobertura=round(relevancia / peso_total, 3))
        )

    resultados.sort(key=lambda r: r["puntaje"], reverse=True)
    return resultados


def recuperar_fragmentos(pregunta: str, limite: int = 3) -> list[Resultado]:
    """Devuelve los fragmentos con evidencia suficiente, del más al menos relevante.

    Si la pregunta no está cubierta por el corpus devuelve una lista vacía.
    """
    resultados = puntuar(pregunta)
    if not resultados or resultados[0]["cobertura"] < UMBRAL_COBERTURA:
        return []

    # Solo fragmentos del documento ganador, para no mezclar temas.
    mejor = resultados[0]
    relevantes = [
        r for r in resultados
        if r["documento"] == mejor["documento"] and r["puntaje"] >= mejor["puntaje"] * 0.75
    ]
    return relevantes[:limite]
