#!/usr/bin/env python3
"""Imprime la sección de CHANGELOG.md de una versión, para usarla como notas de la entrega.

Uso: python scripts/notas_version.py 1.2.0
"""

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def main():
    version = sys.argv[1].removeprefix("v")
    lineas, dentro = [], False
    for linea in (RAIZ / "CHANGELOG.md").read_text(encoding="utf-8").splitlines():
        if linea.startswith("## ["):
            if dentro:
                break
            dentro = linea.startswith(f"## [{version}]")
            continue
        if dentro:
            lineas.append(linea)
    if not dentro and not lineas:
        sys.exit(f"CHANGELOG.md no tiene la versión {version}")
    print("\n".join(lineas).strip())


if __name__ == "__main__":
    main()
