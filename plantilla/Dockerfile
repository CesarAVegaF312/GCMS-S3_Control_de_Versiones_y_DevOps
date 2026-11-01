FROM python:3.13-slim

# El pipeline pasa el commit para que la imagen sepa de dónde salió (trazabilidad).
ARG COMMIT_SHA=local
ENV COMMIT_SHA=${COMMIT_SHA} \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY servicio/ servicio/

RUN useradd --create-home servicio
USER servicio

EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "servicio:create_app()"]
