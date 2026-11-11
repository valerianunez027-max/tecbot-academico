"""Pruebas de la recuperación semántica con ChromaDB (Día 3).

Se omiten si ChromaDB no está instalado o si todavía no se ejecutó scripts/indexar.py.
"""

import pytest

from app import busqueda, vector

pytest.importorskip("chromadb")
pytestmark = pytest.mark.skipif(
    not vector.disponible(), reason="Sin índice: ejecuta python scripts/indexar.py"
)


@pytest.mark.parametrize(
    ("pregunta", "documento"),
    [
        ("¿Qué necesito para iniciar el servicio social?", "servicio-social.md"),
        ("¿Cuáles son las modalidades de titulación?", "titulacion.md"),
    ],
)
def test_chromadb_recupera_el_documento_esperado_en_top3(pregunta, documento):
    resultados = vector.recuperar(pregunta, limite=3)
    assert any(r["documento"] == documento for r in resultados)


def test_resultados_traen_metadatos_y_distancia():
    resultado = vector.recuperar("requisitos del servicio social", limite=1)[0]
    assert {"documento", "tema", "seccion", "texto", "distancia"} <= resultado.keys()
    assert 0 <= resultado["distancia"] <= 2


def test_pregunta_fuera_del_corpus_queda_mas_lejos_que_una_cubierta():
    cubierta = vector.recuperar("¿Qué necesito para iniciar el servicio social?", limite=1)[0]
    fuera = vector.recuperar("¿Cuál es el horario de la cafetería?", limite=1)[0]
    assert fuera["distancia"] > cubierta["distancia"]


# Actividad 6 del tema ChromaDB: la API con ChromaDB cita servicio-social.md
def test_api_con_chromadb_cita_servicio_social(monkeypatch):
    from fastapi.testclient import TestClient

    from app.main import app

    monkeypatch.setenv("TECBOT_MOTOR", "auto")
    respuesta = TestClient(app).post(
        "/api/consulta", json={"pregunta": "¿Qué necesito para iniciar el servicio social?"}
    )
    datos = respuesta.json()
    assert respuesta.status_code == 200
    assert any(f["documento"] == "servicio-social.md" for f in datos["fuentes"])


def test_cafeteria_sigue_sin_fuentes_en_modo_auto(monkeypatch):
    monkeypatch.setenv("TECBOT_MOTOR", "auto")
    fragmentos, motor = busqueda.buscar("¿Cuál es el horario de la cafetería?")
    assert fragmentos == [], f"no debería responder (motor {motor}); ajusta TECBOT_UMBRAL"


# Casos que fallaban con ChromaDB solo (evaluación del 11/11/2026) y que el híbrido corrige.
def test_titularme_cita_titulacion(monkeypatch):
    monkeypatch.setenv("TECBOT_MOTOR", "auto")
    fragmentos, _ = busqueda.buscar("¿Qué necesito para titularme?")
    assert fragmentos and fragmentos[0]["documento"] == "titulacion.md"


def test_costo_de_titulacion_se_abstiene(monkeypatch):
    monkeypatch.setenv("TECBOT_MOTOR", "auto")
    fragmentos, motor = busqueda.buscar("¿Cuánto cuesta la titulación?")
    assert fragmentos == [], f"los documentos no hablan de costos (motor {motor})"
