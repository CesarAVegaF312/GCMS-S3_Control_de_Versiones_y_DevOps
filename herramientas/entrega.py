#!/usr/bin/env python3
"""Métricas de entrega y de prácticas de control de versiones a partir del historial de Git.

Material de la Unidad 3 de GCMS (Gestión de Configuración y Mantenimiento de Software).
Alimenta los formatos F-17 y F-20. Calcula, para un repositorio clonado con su historia completa:

  - etiquetas que cumplen versionamiento semántico y las que no;
  - entregas por año (frecuencia de despliegue, una de las métricas DORA);
  - tiempo de entrega de los cambios: del commit a la primera etiqueta que lo contiene (otra métrica DORA);
  - proporción de versiones de corrección, como aproximación a la tasa de fallos de cambio;
  - mensajes de commit: Conventional Commits, referencias a issues o PR y longitud del asunto;
  - ramas remotas: antigüedad y distancia respecto de la rama principal.

Escribe entregas.csv con una fila por versión. Solo usa la biblioteca estándar de Python 3.8 o posterior y git.

Uso:
  python entrega.py RUTA_DEL_REPOSITORIO [--principal main] [--desde 2022-01-01]
"""

import argparse
import csv
import re
import statistics
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

SEMVER = re.compile(r"^v?(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")
CONVENCIONAL = re.compile(r"^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\([^)]+\))?!?: \S")
REFERENCIA = re.compile(r"#\d+")


def git(repo, *args):
    r = subprocess.run(["git", "-C", str(repo), *args], check=False, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if r.returncode != 0:
        sys.exit(f"Falló: git {' '.join(args)}\n{r.stderr.strip()}")
    return r.stdout


def fecha(ts):
    return datetime.fromtimestamp(int(ts), tz=timezone.utc)


def percentil(datos, p):
    datos = sorted(datos)
    if not datos:
        return None
    k = (len(datos) - 1) * p
    i = int(k)
    return datos[i] + (datos[min(i + 1, len(datos) - 1)] - datos[i]) * (k - i)


def main():
    p = argparse.ArgumentParser(description="Métricas de entrega y de prácticas de control de versiones.")
    p.add_argument("repo", help="ruta del repositorio clonado con historia completa")
    p.add_argument("--principal", default="main", help="rama principal (por defecto main)")
    p.add_argument("--desde", default="", help="considerar solo versiones desde esta fecha, AAAA-MM-DD")
    p.add_argument("--salida", default=".")
    a = p.parse_args()
    repo = Path(a.repo).resolve()
    if git(repo, "rev-parse", "--is-shallow-repository").strip() == "true":
        sys.exit("El repositorio es superficial. Clónelo completo o use: git fetch --unshallow")
    desde = datetime.fromisoformat(a.desde).replace(tzinfo=timezone.utc) if a.desde else None

    # --- etiquetas y versionamiento semántico
    etiquetas = []
    for linea in git(repo, "for-each-ref", "--sort=creatordate", "--format=%(refname:short)\x1f%(creatordate:unix)",
                     "refs/tags").splitlines():
        nombre, ts = linea.split("\x1f")
        etiquetas.append((nombre, fecha(ts)))
    validas = [(n, f) for n, f in etiquetas if SEMVER.match(n)]
    invalidas = [n for n, _ in etiquetas if not SEMVER.match(n)]
    print(f"Etiquetas: {len(etiquetas)} · con versionamiento semántico: {len(validas)}")
    if invalidas:
        print(f"  sin versionamiento semántico: {', '.join(invalidas[:12])}{' …' if len(invalidas) > 12 else ''}")

    entregas = [(n, f) for n, f in validas if "-" not in n and (not desde or f >= desde)]
    if not entregas:
        sys.exit("No hay versiones en el período.")

    # --- frecuencia y tiempo de entrega por versión
    # Cada commit cuenta en la primera versión que lo publicó: se excluye lo que ya estaba en cualquier etiqueta
    # anterior, de cualquier rama. Así las líneas de mantenimiento paralelas no se mezclan.
    filas, todas_horas = [], []
    for nombre, f_entrega in entregas:
        previas = [n for n, f in validas if f < f_entrega]
        tiempos = [int(t) for t in git(repo, "log", "--no-merges", "--format=%ct", nombre,
                                       *(["--not"] + previas if previas else [])).split()]
        horas = [(f_entrega - fecha(t)).total_seconds() / 3600 for t in tiempos]
        horas = [h for h in horas if h >= 0]
        todas_horas += horas
        _, menor, parche = (int(x) for x in SEMVER.match(nombre).groups())
        filas.append({"version": nombre, "fecha": f_entrega.date().isoformat(), "tipo": "corrección" if parche else
                      ("mayor" if menor == 0 else "menor"), "commits": len(horas),
                      "mediana_dias": round(statistics.median(horas) / 24, 1) if horas else "",
                      "p75_dias": round(percentil(horas, 0.75) / 24, 1) if horas else ""})

    salida = Path(a.salida)
    salida.mkdir(parents=True, exist_ok=True)
    with open(salida / "entregas.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0].keys()))
        w.writeheader()
        w.writerows(filas)

    por_anio = Counter(f["fecha"][:4] for f in filas)
    print(f"\nVersiones en el período: {len(filas)} (de {filas[0]['fecha']} a {filas[-1]['fecha']})")
    print("  por año: " + ", ".join(f"{anio}: {n}" for anio, n in sorted(por_anio.items())))
    tipos = Counter(f["tipo"] for f in filas)
    print(f"  mayores: {tipos['mayor']} · menores: {tipos['menor']} · de corrección: {tipos['corrección']}"
          f" ({tipos['corrección'] / len(filas):.0%}; aproximación a la tasa de fallos de cambio)")
    if todas_horas:
        print(f"Tiempo de entrega de los cambios (commit → versión): mediana {statistics.median(todas_horas) / 24:.0f}"
              f" días · percentil 75: {percentil(todas_horas, 0.75) / 24:.0f} días")

    # --- mensajes de commit en el período
    args_log = ["log", "--no-merges", "--format=%s"] + ([f"--since={a.desde}"] if a.desde else [])
    asuntos = [s for s in git(repo, *args_log, a.principal).splitlines() if s.strip()]
    if asuntos:
        conv = sum(1 for s in asuntos if CONVENCIONAL.match(s))
        refs = sum(1 for s in asuntos if REFERENCIA.search(s))
        largos = sum(1 for s in asuntos if len(s) > 72)
        print(f"\nMensajes de commit en {a.principal}: {len(asuntos)}")
        print(f"  Conventional Commits: {conv / len(asuntos):.0%} · con referencia a issue o PR: {refs / len(asuntos):.0%}"
              f" · asunto de más de 72 caracteres: {largos / len(asuntos):.0%}")

    # --- ramas remotas
    ramas = git(repo, "for-each-ref", "--format=%(refname:short)\x1f%(committerdate:short)", "refs/remotes").splitlines()
    ramas = [r.split("\x1f") for r in ramas]
    ramas = [(r, f) for r, f in ramas if "/" in r and not r.endswith("/HEAD")]
    if ramas:
        print("\nRamas remotas (última actividad · commits adelante/atrás de la principal):")
        base = next((r for r, _ in ramas if r.endswith("/" + a.principal)), a.principal)
        for rama, ultima in sorted(ramas, key=lambda r: r[1], reverse=True):
            if rama == base:
                continue
            atras, adelante = git(repo, "rev-list", "--left-right", "--count", f"{base}...{rama}").split()
            print(f"  {rama:<32} {ultima} · {adelante} adelante / {atras} atrás")
    print(f"\nDetalle por versión en {salida / 'entregas.csv'}")


if __name__ == "__main__":
    main()
