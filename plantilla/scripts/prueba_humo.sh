#!/usr/bin/env bash
# Prueba de humo: el servicio responde y es la versión que se espera.
# Uso: scripts/prueba_humo.sh URL_BASE COMMIT_ESPERADO
set -euo pipefail
URL="${1:?Falta la URL base, por ejemplo http://localhost:8000}"
COMMIT="${2:?Falta el commit esperado}"

for intento in $(seq 1 20); do
  if curl -fsS "$URL/salud" > /dev/null 2>&1; then break; fi
  echo "Esperando al servicio (intento $intento)..."
  sleep 1
done

curl -fsS "$URL/salud" | grep -q '"estado":"ok"' || { echo "La ruta /salud no responde ok"; exit 1; }
VERSION=$(curl -fsS "$URL/version")
echo "Respuesta de /version: $VERSION"
echo "$VERSION" | grep -q "\"commit\":\"$COMMIT\"" || { echo "La imagen no corresponde al commit $COMMIT"; exit 1; }
echo "Prueba de humo superada."
