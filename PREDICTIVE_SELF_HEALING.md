## 🔮 Sistema Preditivo de Auto-Healing

Documentação do mecanismo que prevê degradações (latência/erros) e executa mitigação automática, além do suporte a mitigação manual.

### 🎯 Objetivo
Detectar precocemente risco de violação de SLO (latência P95 ou erro %) e acionar automaticamente a rota de mitigação para "resetar" condições artificiais de degradação durante demonstrações.

### 🧠 Visão Geral
| Componente | Função |
|------------|-------|
| `observability/predictive/predictive_monitor.py` | Loop periódico que coleta métricas Prometheus, calcula tendência e decide mitigação |
| `/admin/fault` (manual) | Injeta falhas (latência ou leak de memória artificial) |
| `/admin/mitigate` (manual ou automático) | Remove falhas artificiais: zera latência e limpa leak |
| Logs `mitigation executed` | Eventos unificados (auto ou manual) com `unix_ts` para painel "Última" |
| Logs `manual mitigation executed` | Evento específico da execução manual (painel de contagem) |

### 🔌 Endpoints Administrativos
Requer header: `x-admin-token: secret` (padrão em dev).

1. Injetar latência:
```bash
curl -X POST -H 'x-admin-token: secret' \
  'http://localhost:8000/admin/fault?mode=latency&inc=300'
```
2. Injetar leak de memória (aloca ~KB informados em um chunk):
```bash
curl -X POST -H 'x-admin-token: secret' \
  'http://localhost:8000/admin/fault?mode=leak&kb=50'
```
3. Mitigar (manual):
```bash
curl -X POST -H 'x-admin-token: secret' http://localhost:8000/admin/mitigate
```

### 🧾 Estrutura dos Logs de Mitigação
Exemplos (formato JSON plano):
```json
{"message":"mitigation executed","unix_ts": 1724000000, "ts":"2025-08-18T20:04:58Z","mode":"manual","freed_chunks":1,"reset_latency":true}
{"message":"mitigation executed","unix_ts": 1724000050, "ts":"2025-08-18T20:05:48Z","mode":"auto","metric":"p95_latency","forecast":6500,"threshold":5000}
```

Campos chave:
- `unix_ts`: usado nos painéis "Última Auto" / "Última Manual".
- `mode=manual` ou ausência/`auto` => origem.
- `metric/forecast/threshold`: só em auto.

### 📊 Painéis Principais (Dashboard `predictive-selfheal`)
| Painel | Fonte | Descrição |
|--------|-------|-----------|
| Mitigações Automáticas | Loki | Contagem de logs `mitigation executed` do job `predictive-monitor` |
| Mitigações Manuais | Loki | Contagem de logs `manual mitigation executed` |
| Última Auto | Loki | Timestamp (local) da última mitigação automática (max unix_ts) |
| Última Manual | Loki | Timestamp da última mitigação manual |
| Previsões Executadas | Loki | Contagem de ciclos de previsão (`prediction cycle`) |
| P95 (ms) | Prometheus | Latência P95 (histogram_quantile sobre bucket) |
| Error % | Prometheus | Taxa de erro 5m (increase counters) |
| Req/s | Prometheus | Taxa de requisições (1m rate) |
| Latência & Tráfego | Prometheus | Série com P95 (s), Requests/s, Errors/s |
| Logs: Auto / Manual / Prediction | Loki | Detalhes de cada evento para auditoria |

### 🔍 Consultas LogQL Relevantes
Última mitigação automática:
```
max by () (max_over_time(({job="predictive-monitor"} |= "mitigation executed" | json | unwrap unix_ts)[$__range])) * 1000
```
Mitigações manuais (contagem):
```
count_over_time(({job="product-api"} |= "manual mitigation executed")[$__range])
```

### 🔮 Lógica de Previsão (simplificada)
1. Coleta janelas de métricas (latência p95, erro %, uso de memória).
2. Calcula regressão/tendência para horizonte `PREDICT_HORIZON_SECONDS`.
3. Se previsão > limiar (SLO) em qualquer métrica → chama `/admin/mitigate`.
4. Loga `prediction cycle` com:
   - `breach_any` (bool)
   - `action_taken` (mitigation|none)
   - `since_last_mitigation_sec`

### 🚀 Evolução Recente da Lógica (Anti-Saturação & Precisão)
Resumo rápido (versão aprimorada):
1. Probabilidade agora escala entre `SLO_P95_MS` e `P95_TIMEOUT_MS` (ex: 300ms → 5000ms). Assim só chega a 100% perto do timeout real.
2. Mitigação dispara se qualquer condição ocorrer:
  - Forecast >= `PRE_TIMEOUT_RATIO * P95_TIMEOUT_MS` (mitigação preventiva antes de timeouts reais)
  - Probabilidade >= `PREDICT_PROB_STRONG` E estamos em estado de risco (histerese)
  - Probabilidade na faixa intermediária (`PREDICT_PROB_CONFIRM_MIN` até strong) em **dois ciclos consecutivos** (confirmação dupla)
3. Histerese: Entramos em estado de risco quando forecast > `SLO_P95_MS` e só saímos quando forecast cai abaixo de `SLO_P95_EXIT_MS` (reduz zigue-zague).
4. Gate de qualidade: só consideramos mitigar se `R² >= PREDICT_MIN_R2` (descarta previsões pouco confiáveis).
5. Cooldown continua impedindo mitigação repetida em loop.

Variáveis novas de ajuste rápido:
| Variável | Função | Default |
|----------|--------|---------|
| `P95_TIMEOUT_MS` | Latência onde ocorre timeout real | 5000 |
| `SLO_P95_EXIT_MS` | Limiar de saída da histerese | 90% do SLO |
| `PREDICT_PROB_STRONG` | Probabilidade para disparo direto | 0.6 |
| `PREDICT_PROB_CONFIRM_MIN` | Prob mínima para iniciar confirmação dupla | 0.3 |
| `PREDICT_MIN_R2` | Qualidade mínima da regressão | 0.2 |
| `PREDICT_PRE_TIMEOUT_RATIO` | % do timeout para mitigação antecipada | 0.9 |

Frase de bolso para entrevista:
"A previsão usa regressão linear curta. Escalonamos a probabilidade entre SLO e limite de timeout; aplicamos histerese, confirmação dupla para sinais fracos, corte por R² e mitigação antecipada se o forecast chega a 90% do timeout. Cooldown evita repetição em loop." 

### ⚙️ Variáveis de Ambiente (container `predictive-monitor`)
| Variável | Propósito | Exemplo |
|----------|-----------|---------|
| `PROM_URL` | Endpoint Prometheus | http://prometheus:9090 |
| `TARGET_SERVICE_BASE` | Base da API | http://app:8000 |
| `ADMIN_TOKEN` | Token admin | secret |
| `SLO_P95_MS` | Limiar P95 | 5000 |
| `SLO_ERROR_RATE` | Limiar erro | 0.05 |
| `PREDICT_HORIZON_SECONDS` | Horizonte de previsão | 180 |
| `AUTO_HEAL` | Ativa auto-mitigação (1/0) | 1 |
| `CYCLE_INTERVAL_SECONDS` | Intervalo entre ciclos | 30 |

### ✅ Fluxo de Demonstração Rápida
```bash
# 1. Subir stack
docker compose up -d --build

# 2. Injetar degradação progressiva
for i in 1 2 3; do curl -s -X POST -H 'x-admin-token: secret' \
  "http://localhost:8000/admin/fault?mode=latency&inc=800"; sleep 2; done

# 3. Aguardar ciclo de previsão executar mitigação automática
# (ou disparar manualmente)
curl -X POST -H 'x-admin-token: secret' http://localhost:8000/admin/mitigate
```

### 🧪 Troubleshooting
| Sintoma | Causa Provável | Ação |
|---------|----------------|------|
| Painel "Última Auto" não atualiza | Log sem `unix_ts` ou range muito curto | Verifique log bruto em Loki e aumente o time picker |
| Contagem de Mitigações Manuais não sobe | Header ausente ou token errado | Checar `x-admin-token` e status HTTP | 
| Auto-heal nunca dispara | `AUTO_HEAL=0` ou thresholds altos | Reduzir `SLO_P95_MS` temporariamente |
| Previsões Executadas = 0 | Container `predictive-monitor` não iniciou | `docker compose logs predictive-monitor` |

### 📌 Decisões de Design
- Logs de mitigação manual e automática unificados em evento com `message="mitigation executed"` + campo `mode` para simplificar queries.
- Campos JSON planos (evitando JSON aninhado em `message`).
- Painéis de simulação (latência artificial / leak) removidos para foco em indicadores reais.

---
Última atualização: 18/08/2025
