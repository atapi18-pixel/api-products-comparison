#!/bin/sh
# Script para executar load test a cada 10 minutos

echo "🚀 Iniciando scheduler de load test - execução a cada 10 minutos"

# Loop infinito executando load test a cada 10 minutos
while true; do
  echo "⏰ $(date): Aguardando serviços ficarem prontos..."
  sleep 30  # Aguardar inicial para serviços estarem prontos
  
  echo "🔥 $(date): Iniciando load test com cenários de erro e timeout..."
  k6 run /perf/loadtest.js
  
  echo "✅ $(date): Load test concluído. Próxima execução em 10 minutos..."
  echo "💤 Aguardando 10 minutos para próxima execução..."
  sleep 600  # 10 minutos = 600 segundos
done
