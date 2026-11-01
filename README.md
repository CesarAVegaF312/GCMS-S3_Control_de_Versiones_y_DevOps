# GCMS S3 — Control de Versiones y DevOps

Material de la **Sesión 3** del curso *Gestión de Configuración y Mantenimiento de Software* (GCMS),
Unidad 3: **Control de versiones y automatización (DevOps)**. Maestría en Ingeniería de Software,
Universidad de La Sabana.

Cada grupo implementa, sobre el mismo sistema de las unidades anteriores, la estrategia de gestión de
configuración que diseñó en la Unidad 2:

- un repositorio en Git con la rama principal protegida;
- una estrategia de ramas justificada;
- versionamiento semántico;
- un pipeline de CI/CD que funcione de verdad.

Ese pipeline es la red de seguridad para las mejoras de la Unidad 4.

La actividad de la unidad:

- **Actividad 3. Implementación de control de versiones y automatización (DevOps)** · grupal, de 2 a 3 ·
  **30 %** · 24 horas.
  - **Entregables:**
    - el repositorio del sistema en GitHub o GitLab;
    - un pipeline de CI/CD funcional (construcción, pruebas y despliegue);
    - un documento técnico de **5 a 7 páginas** o un **README.md**;
    - evidencias: capturas, registros de ejecución y commits.
  - Se califica con la rúbrica del aula.
  - **Los formatos F-15 a F-21 no se suben:** son el borrador del documento.

---

## Empiecen aquí

**Todo el material se abre desde aquí, sin descargar nada:**
<https://cesaravegaf312.github.io/GCMS-S3_Control_de_Versiones_y_DevOps/>

1. **Lean el [enunciado](documentos/1_actividad/GCMS_S3_Enunciado_Actividad_3.pdf).**
2. **Copien la [plantilla](plantilla/)** a la raíz del repositorio de su sistema y sigan su
   [README](plantilla/README.md). Trae un pipeline de CI y uno de entrega que ya funcionan.
3. **Lean el [recorrido resuelto](documentos/2_ejemplo/GCMS_S3_Recorrido_Resuelto.pdf).** Muestra las
   ramas, versiones y métricas de Flask, y las ejecuciones reales del pipeline de la plantilla, incluida
   una fallida.
4. **Llenen los [Instrumentos F-15 a F-21](documentos/3_como_se_hace/GCMS_S3_Instrumentos.pdf)**
   mientras trabajan. El F-19, de evidencias, no se puede reconstruir al final.

---

## La plantilla

La carpeta [`plantilla/`](plantilla/) contiene:

- un servicio mínimo en Flask;
- sus pruebas;
- un Dockerfile;
- un registro de cambios;
- tres scripts: `verificar_version.py`, `notas_version.py` y `prueba_humo.sh`;
- dos flujos de GitHub Actions:

| Flujo | Cuándo corre | Trabajos |
|---|---|---|
| `ci.yml` | En cada PR y en cada integración a `main` | calidad (ruff) → pruebas (Python 3.11, 3.12, 3.13) → imagen con prueba de humo |
| `entrega.yml` | Al subir una etiqueta `vX.Y.Z` | verificar → pruebas → publicar la imagen en GHCR → staging → producción con aprobación |

En este repositorio, el flujo [`.github/workflows/plantilla.yml`](.github/workflows/plantilla.yml) corre la
CI de la plantilla cada vez que esta cambia. Sus ejecuciones, en la pestaña **Actions**, son la evidencia
del recorrido resuelto:

- 41256889959: en verde;
- 41257272061: fallida a propósito;
- 41257593217: la corrección, otra vez en verde.

El flujo de entrega no se ejecutó en este repositorio, porque hacerlo publicaría una imagen y una
entrega. Se validó con `actionlint`, y cada pieza se probó por separado: los scripts, la construcción de
la imagen y la prueba de humo.

---

## La herramienta de métricas de entrega

`herramientas/entrega.py` calcula a partir del historial de Git:

- cuántas etiquetas cumplen versionamiento semántico;
- las versiones por año;
- el tiempo de entrega de los cambios, desde el commit hasta la primera versión que lo publicó;
- la proporción de versiones de corrección;
- la convención y las referencias en los mensajes de commit;
- el estado de las ramas remotas.

Escribe `entregas.csv`. Requiere **Python 3.8 o posterior** y **git**, sin bibliotecas externas.

```bash
python herramientas/entrega.py <sistema> --principal main --desde 2026-08-01 --salida salida
```

Las tres primeras métricas son aproximaciones con Git de las métricas DORA de *Accelerate*: frecuencia de
despliegue, tiempo de entrega y tasa de fallos de cambio. La cuarta, el tiempo de restauración, no se ve
en Git.

---

## Estructura del repositorio

```text
GCMS-S3_Control_de_Versiones_y_DevOps/
├── index.html          ← portada: abre desde aquí todo lo demás
├── presentacion.html   ← las 21 diapositivas de la sesión
├── README.md
├── LICENSE
├── plantilla/          ← proyecto con CI/CD para copiar al repositorio del sistema
├── .github/workflows/  ← la CI de la plantilla, corriendo en este repositorio
├── documentos/         ← enunciado, recorrido resuelto, instrumentos y diapositivas (PDF)
├── interactivos/       ← ¿qué versión sigue? y recorrido por el pipeline
├── herramientas/       ← entrega.py
├── ejemplo_flask/      ← el CSV de las métricas de entrega de Flask
└── fuentes/            ← fuentes HTML de los PDF y el script para regenerarlos
```

### La clase

| Archivo | Descripción |
|---|---|
| [`presentacion.html`](presentacion.html) | La sesión en el navegador: 21 diapositivas con índice (**I**), glosario de códigos (**G**), cronómetro del taller (**T**), notas del docente (**N**), modo presentador (**P**) y modo de lectura para el teléfono (**L**). |
| [`documentos/4_clase/GCMS_S3_Deck.pdf`](documentos/4_clase/GCMS_S3_Deck.pdf) | Las mismas diapositivas en PDF. |

### Recursos interactivos — carpeta `interactivos/`

| Archivo | Descripción |
|---|---|
| [`semver_interactivo.html`](interactivos/semver_interactivo.html) | Doce cambios, casi todos del registro de cambios de Flask, para decidir qué número sube bajo SemVer estricto y compararlo con lo que hizo el proyecto. |
| [`pipeline_interactivo.html`](interactivos/pipeline_interactivo.html) | Los dos flujos de la plantilla: se elige qué trae el cambio y se ve en qué etapa se detiene, qué dice el registro y qué se habría entregado sin esa etapa. |

---

## Material de la unidad

**Obligatorio**

- Chacon, S., & Straub, B. (2014). *Pro Git* (2.ª ed.). Apress. Capítulos 3 y 5. https://git-scm.com/book
- Humble, J. (2015). *Continuous delivery* [Grabación de video]. Addison-Wesley Professional. Capítulos 1 a 3.
- GitLab. (2024). *CI/CD documentation*. https://docs.gitlab.com/ee/ci/

**Complementario**

- Docker. *Docker documentation*. https://docs.docker.com
- ThoughtWorks. *Technology Radar*. https://www.thoughtworks.com/radar

---

## Para el docente: regenerar los PDF

```bash
node fuentes/imprimir_pdf.js   # los cuatro PDF; requiere Playwright con Chromium
```

---

## Referencias de la sesión

- Chacon, S., & Straub, B. (2014). *Pro Git* (2.ª ed.). Apress.
- Conventional Commits. (s. f.). *Conventional Commits 1.0.0*. https://www.conventionalcommits.org
- Forsgren, N., Humble, J., & Kim, G. (2018). *Accelerate: The science of lean software and DevOps*. IT Revolution Press.
- Humble, J., & Farley, D. (2010). *Continuous delivery: Reliable software releases through build, test, and deployment automation*. Addison-Wesley.
- Kim, G., Humble, J., Debois, P., & Willis, J. (2016). *The DevOps handbook*. IT Revolution Press.
- Preston-Werner, T. (s. f.). *Semantic Versioning 2.0.0*. https://semver.org

---

## Licencia

Este material se publica bajo la licencia
**[Creative Commons Atribución-NoComercial-CompartirIgual 4.0 Internacional (CC BY-NC-SA 4.0)](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.es)**.
Ver [`LICENSE`](LICENSE).

*Los datos de los ejemplos provienen del repositorio público de [Flask](https://github.com/pallets/flask),
proyecto de Pallets con licencia BSD-3-Clause.*
