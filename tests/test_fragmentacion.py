"""Fragmentación para ChromaDB (no requiere ChromaDB instalado)."""

from app import vector


def test_dividir_texto_respeta_el_tamano():
    texto = "\n\n".join(["párrafo " * 30] * 10)
    partes = vector.dividir_texto(texto, tamano=400, solapamiento=50)
    assert len(partes) > 1
    assert all(len(p) <= 400 + 50 + 2 for p in partes)


def test_preparar_fragmentos_genera_ids_unicos_y_metadatos():
    ids, textos, metadatos = vector.preparar_fragmentos()
    assert len(ids) == len(set(ids)) == len(textos) == len(metadatos)
    assert {m["documento"] for m in metadatos} == {
        "servicio-social.md",
        "residencias-profesionales.md",
        "titulacion.md",
        "acreditacion-academica.md",
    }
    # el texto indexado empieza con el encabezado de su sección
    assert all(t.startswith(m["seccion"]) for t, m in zip(textos, metadatos))
