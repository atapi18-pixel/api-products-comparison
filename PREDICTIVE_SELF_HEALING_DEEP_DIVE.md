# 🔮 Deep Dive – Mecanismo Preditivo de Auto-Healing

Este documento aprofunda a lógica, dados, modelos e estratégia de decisão do subsistema preditivo de mitigação automática.

## 1. Visão Geral Evolutiva
| Fase | Objetivo | Técnica | Complexidade | Status |
|------|----------|---------|--------------|--------|
| F0 (Atual) | Previsão simples de risco | Regressão linear + extrapolação curta | Baixa | Implementável rapidamente |
| F1 | Reduzir falsos positivos | Intervalos de confiança + dupla confirmação | Baixa | Planejado |
| F2 | Capturar sazonalidade curta | Holt-Winters (triple exponential) | Média | Planejado |
| F3 | Robustez streaming | Modelos online (River) – EMA/AdaptiveRegressor | Média | Futuro |
| F4 | Multi-sinal inteligente | Ensemble (latência + erro + volume + mitigations) | Média/Alta | Futuro |
| F5 | Recomendação contextual | Classificador de tipo de degradação | Alta | Futuro |

## 2. Sinais e Fontes de Dados
| Tipo | Métrica / Log | Fonte | Resolução | Uso Preditivo |
|------|---------------|-------|-----------|---------------|
| Latência | P95 derivado de histogram buckets | Prometheus | 15s (scrape) | Target primário de previsão |
| Erro | Taxa de erro (5xx / total) | Prometheus | 15s | Segundo gatilho de risco |
| Tráfego | Requisições por segundo | Prometheus | 15s | Ajustar confiança (volume baixo reduz estabilidade) |
| Estado interno | Mitigações recentes | Logs (Loki) | Eventual | Cooldown e baseline pós-reset |
| Health técnico | Mem usage / CPU (futuro) | Prometheus / Node exporter | 15s | Contexto de saturação |

## 3. Janela Temporal & Amostragem
- Janela móvel (rolling) típica: últimos 5 a 8 minutos (N ~ 20–32 pontos a 15s).
- Horizonte de previsão (look-ahead): 3 × intervalo de coleta (ex: 180s) para antecipar violação antes de impacto perceptível.
- Trade-off: Janela curta = responsivo porém ruidoso; janela longa = estável porém lenta. Escolha inicial: 6 minutos.

## 4. Pipeline de Processamento
1. Coleta: Query PromQL → latência P95 + erro + req/s.
2. Limpeza: Remoção de outliers extremos (IQR ou z-score > 3) opcional.
3. Suavização: EMA (α=0.3) para reduzir jitter.
4. Extração de Features básicas:
   - Tendência (slope) por regressão linear simples.
   - Velocidade relativa (Δ média últimos k vs. média janela total).
   - Aceleração (diferença entre slopes em sub-períodos recentes).
5. Forecast curto:
   - Modelo F0: y(t+h) ≈ y(t) + slope * h.
6. Avaliação de risco:
   - Probabilidade heurística: p = clamp( (forecast - threshold) / threshold , 0, 1 ).
7. Gating / Decisão:
   - Condições: p >= p_min E (cooldown expirado) E (confirmação em 2 ciclos se p marginal).
8. Ação: POST /admin/mitigate (modo auto).
9. Pós-ação:
   - Registrar log
   - Reiniciar baseline (ignorar primeiros N pontos pós-mitigação para evitar ruído de estabilização).

## 5. Modelos – Justificativa
| Modelo | Prós | Contras | Quando usar |
|--------|------|---------|-------------|
| Regressão Linear (slope) | Simples, interpretável | Ignora sazonalidade | Base / MVP |
| Holt-Winters | Captura tendência + sazonalidade | Mais parâmetros | Latência cíclica (picos periódicos) |
| ARIMA (p,d,q) | Rico para autocorrelação | Tunagem cara, sensível a mudança de regime | Séries estáveis longas |
| Prophet | Pouca parametrização | Overkill + dependência extra | Sazonalidade forte (diária) |
| Modelos Online (River) | Adaptação incremental, baixo custo memória | Menos precisão se série muito irregular | Carga contínua variável |
| Ensemble Heurístico | Combina várias visões | Complexidade de manutenção | Fase madura |

Recomendação inicial: slope + Holt-Winters em paralelo (ensemble leve) quando maturar.

## 6. Controle de Falsos Positivos
| Técnica | Descrição | Implementação |
|---------|-----------|---------------|
| Cooldown | Intervalo mínimo entre mitigações | Ex: 2 × horizonte (>= 360s) |
| Dupla Confirmação | Exigir 2 ciclos consecutivos se excesso <10% | Flag transitório |
| Histerese | Threshold de entrada > threshold de saída | Ex: entrar 5000ms, sair < 4500ms |
| Confiança Preditiva | Descartar forecast com R² baixo (<0.3) | Cálculo regressão |
| Volume mínimo | Ignorar se req/s < X (baixa significância estatística) | Checagem prévia |

## 7. Pseudocódigo (F0 → F1)
```python
from dataclasses import dataclass
import time, statistics as stats

@dataclass
class Sample: ts: float; p95: float; err: float; rps: float

WINDOW_SEC = 360
HORIZON_SEC = 180
COOLDOWN_SEC = 360
P95_SLO = 5000
MIN_RPS = 2
P_MIN = 0.15            # prob mínima
P_STRONG = 0.35         # dispara direto

def linear_forecast(samples, horizon):
    # t normalizado
    xs = [(s.ts - samples[0].ts) for s in samples]
    ys = [s.p95 for s in samples]
    n = len(xs)
    mean_x = sum(xs)/n; mean_y = sum(ys)/n
    num = sum((x-mean_x)*(y-mean_y) for x,y in zip(xs,ys))
    den = sum((x-mean_x)**2 for x in xs) or 1e-9
    slope = num/den
    y_future = ys[-1] + slope * horizon
    # r2 simples
    ss_tot = sum((y-mean_y)**2 for y in ys) or 1e-9
    ss_res = sum((y - (mean_y + slope*(x-mean_x)))**2 for x,y in zip(xs,ys))
    r2 = 1 - ss_res/ss_tot
    return y_future, slope, r2

last_mitigation_ts = 0

def decide(samples):
    global last_mitigation_ts
    now = time.time()
    if now - last_mitigation_ts < COOLDOWN_SEC: return False, "cooldown"
    if len(samples) < 8: return False, "warmup"
    if samples[-1].rps < MIN_RPS: return False, "low_rps"
    forecast, slope, r2 = linear_forecast(samples, HORIZON_SEC)
    if r2 < 0.25: return False, "low_conf"
    excess = forecast - P95_SLO
    if excess <= 0: return False, "below_slo"
    p = min(1.0, max(0.0, excess / P95_SLO))
    if p >= P_STRONG:
        last_mitigation_ts = now; return True, f"auto_high p={p:.2f}"
    # weak signal requires confirmation: store state externally
    # (omitted for brevity)
    if p >= P_MIN:
        # Suppose confirm() handles previous cycle memory
        if confirm():
            last_mitigation_ts = now; return True, f"auto_confirmed p={p:.2f}"
        return False, f"await_confirm p={p:.2f}"
    return False, f"low_prob p={p:.2f}"
```

## 8. Estrutura de Logs para Auditoria
Campo adicional sugerido para `prediction cycle`:
```json
{
  "message": "prediction cycle",
  "unix_ts": 1724000500,
  "p95_forecast": 6120,
  "p95_current": 4800,
  "p95_slope": 9.4,
  "p95_r2": 0.62,
  "error_rate_current": 0.021,
  "rps_current": 14.2,
  "probability": 0.22,
  "decision": "await_confirm"
}
```
Para mitigação automática:
```json
{
  "message": "mitigation executed",
  "mode": "auto",
  "unix_ts": 1724000525,
  "reason": "auto_confirmed p=0.37",
  "forecast_exceeded_ms": 1120,
  "cooldown_sec": 360
}
```

## 9. Métricas Customizadas (Prometheus) – Futuro
| Métrica | Tipo | Descrição |
|---------|------|-----------|
| `predict_cycles_total` | Counter | Ciclos de previsão executados |
| `predict_mitigations_total` | Counter | Mitigações automáticas disparadas |
| `predict_forecast_p95_ms` | Gauge | Último forecast de p95 |
| `predict_probability` | Gauge | Última probabilidade calculada |
| `predict_r2` | Gauge | Qualidade da regressão |
| `predict_cooldown_active` | Gauge (0/1) | Indicador de cooldown |

Essas métricas habilitam painéis de qualidade do preditor e tuning continuo.

## 10. Estratégia de Evolução do Modelo
| Passo | Ação | Ganho Esperado |
|-------|------|----------------|
| 1 | Implementar logs enriquecidos + métricas preditivas | Visibilidade interna |
| 2 | Histerese + dupla confirmação | Redução de falsos positivos |
| 3 | Holt-Winters paralelo (comparar MAPE) | Captura melhor de tendência real |
| 4 | Seleção dinâmica de modelo (menor erro janelado) | Robustez adaptativa |
| 5 | Quantile forecasting (intervalos) | Decisão baseada em risco percentílico |
| 6 | Ensemble ponderado por erro recente | Estabilidade |
| 7 | Classificação raiz da degradação (latência vs erro vs saturação) | Mitigações direcionadas |

## 11. Critérios de Avaliação
| Métrica | Descrição | Objetivo Inicial |
|---------|-----------|------------------|
| FPR (False Positive Rate) | Mitigações sem risco real | < 10% |
| FNR (False Negative Rate) | Riscos não mitigados | < 15% |
| Lead Time Médio | Tempo entre previsão e violação evitada | > 30s |
| MTTR Virtual | Tempo até recuperação pós risco detectado | < 40s |
| R² Médio | Qualidade do ajuste regressão | > 0.4 |
| MAPE Forecast | Erro porcentual médio forecast p95 | < 18% |

## 12. Riscos & Mitigações
| Risco | Impacto | Mitigação |
|-------|---------|-----------|
| Mudança brusca no padrão (deploy) | Forecast inválido | Ignorar primeiros N pontos pós-deploy |
| Baixo volume de tráfego | Sinais ruidosos | Limite mínimo de RPS + fallback reativo |
| Deriva de thresholds | Mitigações insuficientes | Ajustar SLO dinamicamente (p95 pctl histórico) |
| Growth de cardinalidade em logs | Custo de armazenamento | Campos fixos e limitados |
| Ação repetitiva em loop | Mitigações redundantes | Cooldown + histerese |

## 13. Próximas Ações Concretas
1. Adicionar métricas `predict_*` (Gauges/Counters) no monitor.
2. Enriquecer log de `prediction cycle` com campos slope / r2 / prob.
3. Implementar confirmação dupla para sinais fracos (estado em memória).
4. Inserir histerese: `SLO_IN = 5000ms`, `SLO_OUT = 4500ms`.
5. Medir MAPE de forecast vs valor real (rolling). Logar a cada N ciclos.

## 14. Resumo Executável (Pitch Curto)
"Modelo linear leve + gating inteligente: probabilidade escalonada SLO→timeout, histerese para estabilidade, confirmação dupla para sinais medianos, mitigação antecipada pré-timeout, checagem de qualidade por R² e cooldown. Resultado: menos saturação a 100% e ações mais precisas." 

---
_Última atualização: 18/08/2025_
