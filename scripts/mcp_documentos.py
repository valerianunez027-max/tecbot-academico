"""Servidor MCP de solo lectura para documentos-demo/ (Día 3 · MCP Filesystem).

Alternativa sin dependencias al servidor oficial @modelcontextprotocol/server-filesystem,
para equipos donde la red bloquea npm. Habla MCP por stdio (JSON-RPC, una línea por mensaje).

Seguridad:
- Solo expone herramientas de LECTURA: no existe ninguna tool para escribir, mover o borrar.
- Toda ruta se resuelve y se rechaza si queda fuera de la carpeta permitida
  (incluye rutas absolutas, "..", y enlaces simbólicos que apunten afuera).

Uso (lo inicia OpenCode, ver opencode.json):
    python scripts/mcp_documentos.py C:\\Proyectos\\tec_bot\\documentos-demo
"""

from __future__ import annotations

import fnmatch
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

NOMBRE = "documentos_academicos"
VERSION = "1.0.0"
MAX_BYTES = 200_000


class AccesoDenegado(Exception):
    pass


class Servidor:
    def __init__(self, raiz: Path) -> None:
        self.raiz = raiz.resolve()
        if not self.raiz.is_dir():
            raise SystemExit(f"La carpeta permitida no existe: {self.raiz}")

    # ------------------------------------------------------------ rutas
    def ruta_segura(self, ruta: str | None) -> Path:
        candidato = Path(ruta or ".")
        if not candidato.is_absolute():
            # Acepta "servicio-social.md" y "documentos-demo/servicio-social.md".
            partes = candidato.parts
            if partes and partes[0] == self.raiz.name:
                candidato = Path(*partes[1:]) if len(partes) > 1 else Path(".")
            candidato = self.raiz / candidato
        resuelta = candidato.resolve()
        if resuelta != self.raiz and self.raiz not in resuelta.parents:
            raise AccesoDenegado(
                f"Acceso denegado: '{ruta}' está fuera de la carpeta permitida ({self.raiz})."
            )
        return resuelta

    def relativa(self, ruta: Path) -> str:
        return ruta.relative_to(self.raiz).as_posix() or "."

    # ------------------------------------------------------------ tools
    def list_allowed_directories(self) -> str:
        return f"Carpeta permitida (solo lectura):\n{self.raiz}"

    def list_directory(self, path: str = ".") -> str:
        carpeta = self.ruta_segura(path)
        if not carpeta.is_dir():
            raise ValueError(f"No es una carpeta: {path}")
        lineas = [
            f"[{'DIR' if e.is_dir() else 'FILE'}] {e.name}"
            for e in sorted(carpeta.iterdir(), key=lambda e: (not e.is_dir(), e.name.lower()))
        ]
        return "\n".join(lineas) or "(carpeta vacía)"

    def read_text_file(self, path: str, head: int | None = None) -> str:
        archivo = self.ruta_segura(path)
        if not archivo.is_file():
            raise ValueError(f"No existe el archivo: {path}")
        if archivo.stat().st_size > MAX_BYTES:
            raise ValueError(f"Archivo demasiado grande (> {MAX_BYTES} bytes).")
        texto = archivo.read_text(encoding="utf-8")
        if head:
            texto = "\n".join(texto.splitlines()[: int(head)])
        return texto

    def search_files(self, pattern: str) -> str:
        patron = pattern if any(c in pattern for c in "*?[") else f"*{pattern}*"
        encontrados = [
            self.relativa(p)
            for p in sorted(self.raiz.rglob("*"))
            if p.is_file() and fnmatch.fnmatch(p.name.lower(), patron.lower())
        ]
        return "\n".join(encontrados) or "Sin coincidencias."

    def get_file_info(self, path: str) -> str:
        ruta = self.ruta_segura(path)
        if not ruta.exists():
            raise ValueError(f"No existe: {path}")
        info = ruta.stat()
        return "\n".join(
            [
                f"ruta: {self.relativa(ruta)}",
                f"tipo: {'carpeta' if ruta.is_dir() else 'archivo'}",
                f"tamaño: {info.st_size} bytes",
                f"modificado: {datetime.fromtimestamp(info.st_mtime).isoformat(timespec='seconds')}",
                "permisos: solo lectura (este servidor no puede escribir)",
            ]
        )


HERRAMIENTAS: list[dict[str, Any]] = [
    {
        "name": "list_allowed_directories",
        "description": "Muestra la única carpeta a la que este servidor tiene acceso (solo lectura).",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "list_directory",
        "description": "Lista archivos y carpetas dentro de documentos-demo/. Ruta relativa; '.' es la raíz.",
        "inputSchema": {
            "type": "object",
            "properties": {"path": {"type": "string", "description": "Ruta relativa, por defecto '.'"}},
        },
    },
    {
        "name": "read_text_file",
        "description": "Lee un documento de texto de documentos-demo/ (por ejemplo 'servicio-social.md').",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Ruta del archivo dentro de documentos-demo/"},
                "head": {"type": "integer", "description": "Opcional: solo las primeras N líneas"},
            },
            "required": ["path"],
        },
    },
    {
        "name": "search_files",
        "description": "Busca archivos por nombre dentro de documentos-demo/ (texto o patrón tipo '*.md').",
        "inputSchema": {
            "type": "object",
            "properties": {"pattern": {"type": "string"}},
            "required": ["pattern"],
        },
    },
    {
        "name": "get_file_info",
        "description": "Muestra tamaño y fecha de modificación de un archivo de documentos-demo/.",
        "inputSchema": {
            "type": "object",
            "properties": {"path": {"type": "string"}},
            "required": ["path"],
        },
    },
]


# ---------------------------------------------------------------- protocolo
def responder(id_: Any, resultado: Any = None, error: dict[str, Any] | None = None) -> None:
    mensaje: dict[str, Any] = {"jsonrpc": "2.0", "id": id_}
    if error is not None:
        mensaje["error"] = error
    else:
        mensaje["result"] = resultado
    sys.stdout.buffer.write(json.dumps(mensaje, ensure_ascii=False).encode("utf-8") + b"\n")
    sys.stdout.buffer.flush()


def manejar(servidor: Servidor, mensaje: dict[str, Any]) -> None:
    metodo = mensaje.get("method")
    id_ = mensaje.get("id")
    params = mensaje.get("params") or {}

    if id_ is None:  # notificación (p. ej. notifications/initialized): no se responde
        return

    if metodo == "initialize":
        responder(
            id_,
            {
                "protocolVersion": params.get("protocolVersion", "2025-06-18"),
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": NOMBRE, "version": VERSION},
                "instructions": "Acceso de solo lectura a los documentos de demostración de TecBot.",
            },
        )
    elif metodo == "ping":
        responder(id_, {})
    elif metodo == "tools/list":
        responder(id_, {"tools": HERRAMIENTAS})
    elif metodo == "tools/call":
        nombre = params.get("name")
        argumentos = params.get("arguments") or {}
        if nombre not in {h["name"] for h in HERRAMIENTAS}:
            responder(id_, {"content": [{"type": "text", "text": f"Herramienta no disponible: {nombre}. "
                                         "Este servidor es de solo lectura."}], "isError": True})
            return
        try:
            texto = getattr(servidor, nombre)(**argumentos)
            responder(id_, {"content": [{"type": "text", "text": texto}], "isError": False})
        except (AccesoDenegado, ValueError, TypeError, OSError) as error:
            responder(id_, {"content": [{"type": "text", "text": str(error)}], "isError": True})
    elif metodo in ("resources/list", "prompts/list"):
        responder(id_, {metodo.split("/")[0]: []})
    else:
        responder(id_, error={"code": -32601, "message": f"Método no soportado: {metodo}"})


def main() -> None:
    raiz = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "documentos-demo"
    servidor = Servidor(raiz)
    print(f"Servidor MCP '{NOMBRE}' (solo lectura) en stdio. Carpeta: {servidor.raiz}", file=sys.stderr, flush=True)
    for linea in sys.stdin.buffer:
        linea = linea.strip()
        if not linea:
            continue
        try:
            mensaje = json.loads(linea.decode("utf-8"))
        except json.JSONDecodeError:
            responder(None, error={"code": -32700, "message": "JSON inválido"})
            continue
        manejar(servidor, mensaje)


if __name__ == "__main__":
    main()
