"""Contrato de la API de consulta (ver documentacion/arquitectura.md)."""

from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints

LONGITUD_MAXIMA_PREGUNTA = 1000

Pregunta = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=LONGITUD_MAXIMA_PREGUNTA),
]


class ConsultaEntrada(BaseModel):
    pregunta: Pregunta = Field(
        description="Pregunta en lenguaje natural (1 a 1,000 caracteres).",
        examples=["¿Qué necesito para el servicio social?"],
    )


class Fuente(BaseModel):
    documento: str = Field(description="Archivo de documentos-demo/ que respalda la respuesta.")
    tema: str
    seccion: str
    fragmento: str = Field(description="Extracto del documento citado.")


class ConsultaSalida(BaseModel):
    respuesta: str
    fuentes: list[Fuente]
    advertencia: str | None = None
