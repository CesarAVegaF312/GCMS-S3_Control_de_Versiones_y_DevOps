import re

import pytest

from servicio import __version__, create_app


@pytest.fixture
def cliente():
    return create_app().test_client()


def test_salud(cliente):
    respuesta = cliente.get("/salud")
    assert respuesta.status_code == 200
    assert respuesta.get_json() == {"estado": "ok"}


def test_version_es_semver(cliente):
    datos = cliente.get("/version").get_json()
    assert datos["version"] == __version__
    assert re.fullmatch(r"\d+\.\d+\.\d+", datos["version"])


def test_saludo(cliente):
    assert cliente.get("/saludo/Ana").get_json() == {"mensaje": "Hola, Ana"}
