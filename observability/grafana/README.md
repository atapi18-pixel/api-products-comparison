## 📊 Grafana - Provisionamento & Dashboards

Este diretório contém provisionamento automático de datasources e dashboards para observabilidade completa (Métricas, Logs, Traces e Alertas).

## 🗂️ Estrutura
```
observability/grafana/
├── dashboards/                    # JSON dos dashboards
├── provisioning/
│   ├── dashboards/                # Regras de provisionamento de dashboards
│   └── datasources/               # Datasources (Prometheus, Loki, Tempo)
└── notification/                  # (placeholder) canais de notificação adicionais
```

## 📌 Dashboards Principais
- `products-dashboard.json`: Métricas RED / USE / Golden Signals + Logs + Traces
- `predictive-selfheal.json`: Auto-healing preditivo (mitigações, previsões, performance)

## 🔌 Datasources Provisionados
| Serviço | UID | URL | Observação |
|---------|-----|-----|-----------|
| Prometheus | `prom` | http://prometheus:9090 | Métricas (PromQL) |
| Loki | `loki` | http://loki:3100 | Logs (LogQL) |
| Tempo | `tempo` | http://tempo:3200 | Traces (TraceQL) |

Se o UID diferir em outra instância, ajuste o campo `datasource.uid` dentro dos arquivos JSON correspondentes.

## 🔍 Logs (Live Tail)
O painel de live logs usa a query padrão `{job="varlogs"}`.
Se seus labels diferirem, substitua por algo como `{app="product-api"}` ou revise a configuração do Fluent Bit/Promtail.

## ▶️ Executando Localmente
```bash
docker compose up -d --build
# Acesse: http://localhost:3000  (admin / admin)
```

## ♻️ Atualizando Dashboards
1. Edite no Grafana UI
2. Use "Export > View JSON"
3. Substitua o arquivo em `dashboards/`
4. Faça commit no repositório
5. (Opcional) Reinicie o container Grafana se auto-refresh não detectar mudança:
```bash
docker compose restart grafana
```

## 🛠️ Ajustes Comuns
| Problema | Causa | Solução |
|----------|-------|---------|
| Dashboard sem dados | Datasource errado ou UID divergente | Verifique `Configuration > Data sources` |
| Painel de logs vazio | Label não corresponde ao pipeline | Ajuste a query LogQL |
| Traces não aparecem | Otel Collector não exportando | Verifique logs do `otel-collector` |
| Erro de permissão Loki | Volume com owner incorreto | Ajustar permissões ou rodar como root só em dev |

## 🧪 Verificação Rápida
```bash
curl -s http://localhost:9090/-/ready   # Prometheus
curl -s http://localhost:3100/ready     # Loki
curl -s http://localhost:3200/status    # Tempo
```

## 🔐 Produção (Recomendações)
- Habilitar autenticação externa (OAuth / SSO)
- Ajustar retenção no Loki / Tempo
- Dashboards versionados via CI/CD
- Criar pasta de dashboards segregada por domínio

---
_Última atualização: 18/08/2025_
