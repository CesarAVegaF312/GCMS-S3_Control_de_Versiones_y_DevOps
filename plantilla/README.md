# Plantilla de proyecto con CI/CD

Plantilla de la Unidad 3 de GCMS. Trae un servicio mínimo y, alrededor de él, lo que la Actividad 3 pide
implementar:

- pruebas automáticas;
- revisión de estilo;
- una imagen de contenedor;
- verificación de versiones;
- un pipeline de integración continua;
- un pipeline de entrega con staging y aprobación para producción.

El servicio es lo de menos: cada grupo lo reemplaza por su sistema y conserva la estructura.

## Cómo usarla

1. Copien el contenido de esta carpeta a la **raíz** del repositorio de su sistema, incluida la carpeta oculta
   `.github/`. Los flujos solo corren si `.github/workflows/` está en la raíz.
2. Reemplacen `servicio/` por su sistema y `tests/` por sus pruebas. Si el sistema no es Python, conserven
   los trabajos de los flujos y cambien los comandos de instalación, pruebas y construcción.
3. En GitHub, configuren:
   - **Settings → Branches**: proteger `main`, exigir PR y que la verificación de CI pase antes de integrar.
   - **Settings → Environments**: crear `staging` y `produccion`. En `produccion`, agregar quién debe aprobar.
   - **Settings → Actions → General**: en *Workflow permissions*, permitir lectura y escritura, para que el
     flujo de entrega pueda publicar la imagen y la entrega.
4. Abran un PR con un cambio pequeño y vean correr la CI.

## Qué hay

| Ruta | Para qué |
|---|---|
| `servicio/` | El servicio de ejemplo: `/salud`, `/version` y `/saludo/<nombre>` |
| `tests/` | Pruebas con pytest |
| `scripts/verificar_version.py` | Antes de entregar: la etiqueta tiene formato `vMAYOR.MENOR.PARCHE`, coincide con la versión declarada y tiene sección en el registro de cambios |
| `scripts/notas_version.py` | Extrae del registro de cambios las notas de una versión |
| `scripts/prueba_humo.sh` | Comprueba que el servicio desplegado responde y es el commit esperado |
| `Dockerfile` | Imagen del servicio, con un usuario sin privilegios y el commit en la variable `COMMIT_SHA` |
| `CHANGELOG.md` | Registro de cambios en formato Keep a Changelog |
| `.github/workflows/ci.yml` | En cada PR y en cada integración a `main`: calidad, pruebas en tres versiones de Python e imagen con prueba de humo |
| `.github/workflows/entrega.yml` | En cada etiqueta `vX.Y.Z`: verificar, pruebas, publicar la imagen, staging y producción con aprobación |

## Trabajo diario

```bash
python -m venv .venv && source .venv/bin/activate        # en Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
ruff check . && ruff format --check . && pytest           # lo mismo que corre la CI
flask --app "servicio:create_app()" run                    # el servicio en http://127.0.0.1:5000
```

## Publicar una versión

1. Suban la versión en `pyproject.toml` y en `servicio/__init__.py`.
2. Muevan lo de «Sin publicar» a una sección nueva en `CHANGELOG.md`, con la versión y la fecha.
3. Integren esos cambios a `main` por PR.
4. Creen la etiqueta y súbanla:

```bash
python scripts/verificar_version.py v0.2.0     # lo mismo que hará el pipeline
git tag -a v0.2.0 -m "Versión 0.2.0"
git push origin v0.2.0
```

El flujo de entrega:

- construye la imagen **una sola vez**;
- la publica en GitHub Container Registry con la versión y el commit como etiquetas;
- despliega en staging esa misma imagen, identificada por su digest, y la prueba;
- espera la aprobación de producción y publica la entrega con las notas del registro de cambios.

En la plantilla, «producción» es publicar la entrega. Si su sistema tiene un servidor, ese trabajo es el que
despliega allí.

## Decisiones que la plantilla ya tomó

- **Acciones fijadas por hash de commit, no por etiqueta.** Una etiqueta como `v7` puede apuntar mañana a
  otro código; un hash no. Es la integridad del pipeline de la Unidad 2.
- **Dependencias con versión exacta.** Lo que se prueba es lo que se construye.
- **Permisos mínimos.** Los flujos solo leen el repositorio, salvo los trabajos que publican.
- **Ningún secreto en el repositorio.** El único que se usa es el `GITHUB_TOKEN` que GitHub entrega a cada
  ejecución.

## Licencia

Material docente de GCMS, Universidad de La Sabana, bajo licencia CC BY-NC-SA 4.0. Pueden copiar esta
plantilla en el repositorio de su sistema para el curso.
