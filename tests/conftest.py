"""Configuración común de pruebas.

Las pruebas de contrato (test_consulta.py) usan la búsqueda por palabras clave para
ser deterministas. ChromaDB se prueba aparte en test_vector.py.
"""

import os

os.environ.setdefault("TECBOT_MOTOR", "palabras")
os.environ.setdefault("TECBOT_GENERADOR", "extractivo")
