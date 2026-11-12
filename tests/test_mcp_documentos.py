"""Pruebas del servidor MCP de solo lectura (scripts/mcp_documentos.py).

Se arranca el servidor como lo hace OpenCode (proceso por stdio) y se le habla en JSON-RPC.
Cubren las pruebas de seguridad del tema "MCP Filesystem con acceso restringido".
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
SERVIDOR = RAIZ / "scripts" / "mcp_documentos.py"
DOCUMENTOS = RAIZ / "documentos-demo"


@pytest.fixture()
def mcp():
    proceso = subprocess.Popen(
        [sys.executable, str(SERVIDOR), str(DOCUMENTOS)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    contador = {"id": 0}

    def llamar(metodo, params=None):
        contador["id"] += 1
        mensaje = {"jsonrpc": "2.0", "id": contador["id"], "method": metodo, "params": params or {}}
        proceso.stdin.write(json.dumps(mensaje).encode("utf-8") + b"\n")
        proceso.stdin.flush()
        return json.loads(proceso.stdout.readline().decode("utf-8"))

    llamar("initialize", {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "pytest"}})
    proceso.stdin.write(b'{"jsonrpc":"2.0","method":"notifications/initialized"}\n')
    proceso.stdin.flush()
    yield llamar
    proceso.stdin.close()
    proceso.wait(timeout=5)


def texto(respuesta):
    return respuesta["result"]["content"][0]["text"]


def test_solo_expone_herramientas_de_lectura(mcp):
    nombres = {h["name"] for h in mcp("tools/list")["result"]["tools"]}
    assert "read_text_file" in nombres and "list_directory" in nombres
    assert not nombres & {"write_file", "edit_file", "move_file", "create_directory"}


# MCP-01: listar carpeta permitida
def test_lista_los_cuatro_documentos(mcp):
    salida = texto(mcp("tools/call", {"name": "list_directory", "arguments": {"path": "."}}))
    for nombre in ("servicio-social.md", "residencias-profesionales.md", "titulacion.md", "acreditacion-academica.md"):
        assert nombre in salida


# MCP-02: leer documento permitido
def test_lee_un_documento_permitido(mcp):
    respuesta = mcp("tools/call", {"name": "read_text_file", "arguments": {"path": "servicio-social.md", "head": 3}})
    assert respuesta["result"]["isError"] is False
    assert "Servicio social" in texto(respuesta)


# MCP-03: leer fuera de la carpeta
@pytest.mark.parametrize(
    "ruta",
    [
        "../AGENTS.md",
        "../.gitignore",
        str(RAIZ / "README.md"),
        "C:\\Windows\\System32\\drivers\\etc\\hosts",
        "/etc/hosts",
    ],
)
def test_rechaza_rutas_fuera_de_la_carpeta(mcp, ruta):
    respuesta = mcp("tools/call", {"name": "read_text_file", "arguments": {"path": ruta}})
    assert respuesta["result"]["isError"] is True


# MCP-04: escribir en la carpeta
def test_no_existe_herramienta_de_escritura(mcp):
    respuesta = mcp("tools/call", {"name": "write_file", "arguments": {"path": "prueba.txt", "content": "x"}})
    assert respuesta["result"]["isError"] is True
    assert not (DOCUMENTOS / "prueba.txt").exists()
