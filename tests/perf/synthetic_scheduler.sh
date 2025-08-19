#!/bin/sh
# Loop contínuo para rodar synthetic.js em sessões de 1h (para evitar leaks de memória na própria k6 se houver)

if grep -q $'\r' "$0"; then
  echo "Normalizando CRLF -> LF (synthetic_scheduler.sh)" >&2
  tmp=$(mktemp)
  tr -d '\r' < "$0" > "$tmp"
  chmod +x "$tmp"
  exec /bin/sh "$tmp" "$@"
fi

echo "🚀 Iniciando synthetic scheduler (sessões de 1h)"

while true; do
  echo "⏰ $(date): start synthetic batch"
  k6 run /perf/synthetic.js --duration 1h || echo "⚠️ k6 retornou código $?"
  echo "🔁 Reiniciando próxima sessão em 5s"
  sleep 5
done
