#!/usr/bin/env python3
"""Verifica que una etiqueta de entrega sea coherente con el repositorio antes de publicar.

Uso: python scripts/verificar_version.py v1.2.0

Comprueba cuatro cosas y falla si alguna no se cumple:
  1. la etiqueta sigue el formato vMAYOR.MENOR.PARCHE de versionamiento semántico;
  2. pyproject.toml declara la misma versión;
  3. servicio/__init__.py declara la misma versión;
  4. CHANGELOG.md tiene una sección para esa versión.
"""

import re
import sys
import tomllib
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SEMVER = re.compile(r"v(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)")


def main():
    if len(sys.argv) != 2:
        sys.exit("Uso: python scripts/verificar_version.py vMAYOR.MENOR.PARCHE")
    etiqueta = sys.argv[1]
    errores = []

    if not SEMVER.fullmatch(etiqueta):
        errores.append(f"La etiqueta «{etiqueta}» no tiene el formato vMAYOR.MENOR.PARCHE")
    version = etiqueta.removeprefix("v")

    proyecto = tomllib.loads((RAIZ / "pyproject.toml").read_text(encoding="utf-8"))
    declarada = proyecto["project"]["version"]
    if declarada != version:
        errores.append(f"pyproject.toml declara {declarada}, no {version}")

    fuente = (RAIZ / "servicio" / "__init__.py").read_text(encoding="utf-8")
    codigo = re.search(r'__version__\s*=\s*"([^"]+)"', fuente)
    en_codigo = codigo.group(1) if codigo else "nada"
    if en_codigo != version:
        errores.append(f"servicio/__init__.py declara {en_codigo}, no {version}")

    if f"## [{version}]" not in (RAIZ / "CHANGELOG.md").read_text(encoding="utf-8"):
        errores.append(f"CHANGELOG.md no tiene una sección «## [{version}]»")

    if errores:
        print("La etiqueta no se puede publicar:")
        for e in errores:
            print(f"  - {e}")
        sys.exit(1)
    print(f"{etiqueta}: formato, versión declarada y registro de cambios coinciden.")


if __name__ == "__main__":
    main()
