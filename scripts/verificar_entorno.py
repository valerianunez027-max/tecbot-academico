"""Verifica que ChromaDB y Ollama estén listos para el Día 3.

Uso (desde la raíz del proyecto, con el entorno virtual activo):
    python scripts/verificar_entorno.py
"""

import sys

MODELO_OLLAMA = "llama3.2:3b"
ok = True


def paso(titulo: str) -> None:
    print(f"\n== {titulo}")


paso("1. ChromaDB instalado")
try:
    import chromadb

    print(f"   OK  chromadb {chromadb.__version__}")
except ImportError:
    print("   FALLA  No está instalado. Ejecuta: pip install -r requirements.txt")
    sys.exit(1)

paso("2. Embeddings locales de ChromaDB (la primera vez descarga ~80 MB)")
try:
    cliente = chromadb.EphemeralClient()
    coleccion = cliente.get_or_create_collection("prueba_entorno", metadata={"hnsw:space": "cosine"})
    coleccion.upsert(
        ids=["a", "b"],
        documents=[
            "Requisitos para iniciar el servicio social.",
            "Modalidades de titulación: tesis, tesina y proyecto integrador.",
        ],
    )
    resultado = coleccion.query(query_texts=["¿Qué necesito para el servicio social?"], n_results=1)
    mejor = resultado["ids"][0][0]
    print(f"   OK  búsqueda semántica funcionando (resultado: '{mejor}')")
    if mejor != "a":
        print("   AVISO  se esperaba 'a'; revisa el modelo de embeddings")
except Exception as error:  # noqa: BLE001 - se informa cualquier fallo al usuario
    ok = False
    print(f"   FALLA  {type(error).__name__}: {error}")

paso(f"3. Ollama corriendo y modelo {MODELO_OLLAMA}")
try:
    import ollama

    respuesta = ollama.list()
    modelos = [getattr(m, "model", None) or m.get("model") or m.get("name") for m in respuesta["models"]]
    print(f"   OK  Ollama responde. Modelos: {', '.join(modelos) or '(ninguno)'}")
    if not any(str(m).startswith(MODELO_OLLAMA) for m in modelos):
        ok = False
        print(f"   FALTA  Ejecuta: ollama pull {MODELO_OLLAMA}")
except ImportError:
    ok = False
    print("   FALLA  Falta la librería: pip install -r requirements.txt")
except Exception as error:  # noqa: BLE001
    ok = False
    print(f"   FALLA  No se pudo conectar con Ollama ({error}). Ábrelo desde el menú Inicio.")

print("\n" + ("Todo listo para el Día 3." if ok else "Hay pasos pendientes; revisa los mensajes de arriba."))
sys.exit(0 if ok else 1)
