"""Consulta ChromaDB y muestra los fragmentos más cercanos con su distancia.

Uso:
    python scripts/consultar.py "¿Qué necesito para iniciar el servicio social?"
    python scripts/consultar.py "¿Cuáles son las modalidades de titulación?" --ollama
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import config, vector  # noqa: E402
from app.busqueda import buscar  # noqa: E402
from app.generacion import generar_con_modelo, generar_respuesta  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Consulta el índice de TecBot.")
    parser.add_argument("pregunta", nargs="?", default="¿Qué necesito para iniciar el servicio social?")
    parser.add_argument("-k", type=int, default=4, help="Fragmentos a recuperar (default 4)")
    parser.add_argument("--ollama", action="store_true", help=f"Redactar con {config.modelo_ollama()}")
    args = parser.parse_args()

    if not vector.disponible():
        print("No hay índice de ChromaDB. Ejecuta primero: python scripts/indexar.py")
        sys.exit(1)

    print(f"Pregunta: {args.pregunta}\n")
    print(f"Top-{args.k} de ChromaDB (distancia coseno; menor = más parecido, umbral {config.umbral_distancia()}):")
    for r in vector.recuperar(args.pregunta, limite=args.k):
        marca = "OK" if r["distancia"] <= config.umbral_distancia() else "--"
        print(f"\n {marca} [{r['documento']} · {r['seccion']} · distancia {r['distancia']:.3f}]")
        print("   " + r["texto"][:300].replace("\n", "\n   "))

    fragmentos, motor = buscar(args.pregunta)
    print(f"\n--- Respuesta (motor: {motor}) ---")
    if args.ollama and fragmentos:
        print(generar_con_modelo(args.pregunta, fragmentos))
    else:
        print(generar_respuesta(args.pregunta, fragmentos))


if __name__ == "__main__":
    main()
