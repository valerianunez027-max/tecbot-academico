"""API de TecBot Académico.

Ejecutar desde la raíz del proyecto:
    uvicorn app.main:app --reload
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.generacion import (
    ADVERTENCIA_SIN_EVIDENCIA,
    RESPUESTA_SIN_EVIDENCIA,
    generar_respuesta,
    resumir_fragmento,
)
from app.rag import recuperar_fragmentos
from app.schemas import ConsultaEntrada, ConsultaSalida, Fuente

CARPETA_LANDING = Path(__file__).resolve().parent.parent / "tecbot-landing"

app = FastAPI(
    title="TecBot Académico",
    description="Asistente de información académica (prototipo didáctico, documentos ficticios).",
    version="0.2.0",
)

# CORS restringido: la landing abierta con doble clic (origen "null") y servidores locales.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "null",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
    ],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.get("/salud")
def salud() -> dict[str, str]:
    return {"estado": "ok"}


@app.post("/api/consulta", response_model=ConsultaSalida)
def consultar(entrada: ConsultaEntrada) -> ConsultaSalida:
    fragmentos = recuperar_fragmentos(entrada.pregunta, limite=3)

    if not fragmentos:
        return ConsultaSalida(
            respuesta=RESPUESTA_SIN_EVIDENCIA,
            fuentes=[],
            advertencia=ADVERTENCIA_SIN_EVIDENCIA,
        )

    fuentes = [
        Fuente(
            documento=f["documento"],
            tema=f["tema"],
            seccion=f["seccion"],
            fragmento=resumir_fragmento(f),
        )
        for f in fragmentos
    ]
    return ConsultaSalida(
        respuesta=generar_respuesta(entrada.pregunta, fragmentos),
        fuentes=fuentes,
        advertencia=None,
    )


# La landing se sirve en http://localhost:8000/ . Se monta al final para no tapar las rutas de la API.
if CARPETA_LANDING.is_dir():
    app.mount("/", StaticFiles(directory=CARPETA_LANDING, html=True), name="landing")
