"""Indexa documentos-demo/ en ChromaDB (Día 3).

Uso, desde la raíz del proyecto con el entorno virtual activo:
    python scripts/indexar.py

Vuelve a ejecutarlo cada vez que cambien los documentos: borra y reconstruye la colección.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import config, vector  # noqa: E402


def main() -> None:
    ids, _, metadatos = vector.preparar_fragmentos()
    por_documento: dict[str, int] = {}
    for meta in metadatos:
        por_documento[meta["documento"]] = por_documento.get(meta["documento"], 0) + 1

    print("Indexando (la primera vez puede tardar mientras carga el modelo de embeddings)...")
    total = vector.construir_indice()

    print(f"\nFragmentos indexados: {len(ids)}")
    for documento, cantidad in sorted(por_documento.items()):
        print(f"  - {documento}: {cantidad}")
    print(f"Colección: {config.COLECCION}")
    print(f"Total en la colección: {total}")
    print(f"Carpeta: {config.CARPETA_CHROMA}")


if __name__ == "__main__":
    main()
