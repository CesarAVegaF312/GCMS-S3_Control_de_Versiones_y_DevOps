"""Servicio de ejemplo de la plantilla de la Unidad 3.

Es intencionalmente pequeño: lo que importa es el repositorio y el pipeline que lo rodean.
Cada grupo lo reemplaza por su propio sistema.
"""

import os

from flask import Flask, jsonify

__version__ = "0.1.0"


def create_app():
    app = Flask(__name__)

    @app.get("/salud")
    def salud():
        return jsonify(estado="OK")

    @app.get("/version")
    def version():
        # El commit lo inyecta el pipeline al construir la imagen; en local no existe.
        return jsonify(version=__version__, commit=os.environ.get("COMMIT_SHA", "local"))

    @app.get("/saludo/<nombre>")
    def saludo(nombre):
        return jsonify(mensaje=f"Hola, {nombre}")

    return app
