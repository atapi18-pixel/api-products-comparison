#!/bin/sh
# Script para executar load test a cada 30 minutos

# --- Normalização de CRLF (executa só se arquivo ainda tiver \r) ---
if grep -q $'\r' "$0"; then
  echo "Normalizando CRLF -> LF (scheduler.sh)" >&2
  tmp=$(mktemp)
  tr -d '\r' < "$0" > "$tmp"
  chmod +x "$tmp"
  exec /bin/sh "$tmp" "$@"
fi

echo "🚀 Iniciando scheduler de load test - execução a cada 30 minutos"

# Loop infinito executando load test a cada 30 minutos
while true; do
  echo "⏰ $(date): Aguardando serviços ficarem prontos..."
  sleep 30  # Aguardar inicial para serviços estarem prontos

  echo "🔥 $(date): Iniciando load test com cenários de erro e timeout..."
  k6 run /perf/loadtest.js

  echo "✅ $(date): Load test concluído. Próxima execução em 30 minutos..."
  echo "💤 Aguardando 30 minutos para próxima execução..."
  sleep 1800  # 30 minutos = 1800 segundos
done
