"""Pruebas de la redacción extractiva (no dependen de FastAPI)."""

from app.generacion import (
    RESPUESTA_SIN_EVIDENCIA,
    generar_respuesta,
    limpiar_markdown,
    recortar,
)
from app.rag import recuperar_fragmentos


def test_sin_fragmentos_responde_que_no_hay_informacion():
    assert generar_respuesta("lo que sea", []) == RESPUESTA_SIN_EVIDENCIA


def test_respuesta_cita_el_documento_y_conserva_requisitos():
    pregunta = "¿Qué necesito para el servicio social?"
    respuesta = generar_respuesta(pregunta, recuperar_fragmentos(pregunta))
    assert "servicio-social.md" in respuesta
    assert "60% de los créditos" in respuesta


def test_limpiar_markdown_convierte_tablas_y_quita_negritas():
    texto = "| Documento | Formato |\n|---|---|\n| **Solicitud** | SS-01 |"
    assert limpiar_markdown(texto) == "- Documento · Formato\n- Solicitud · SS-01"


def test_recortar_no_corta_palabras():
    resultado = recortar("uno dos tres cuatro cinco", 12)
    assert resultado.endswith("…")
    assert len(resultado) <= 14
