# Pitch Técnico – Products API + Observabilidade Preditiva

Formato: Markdown para apresentação em uma única tela (VS Code Preview).
Tempo alvo: 18–20 minutos (±50s por slide de conteúdo + 5 min demo + Q&A).

---
## Slide 1 – Título & Posicionamento
**Products API** – Arquitetura Hexagonal + Observabilidade 360° + Auto-Healing Preditivo.
Mensagem-chave: Não só construir; elevar confiabilidade e antecipar falhas.
Fala curta: “Vou mostrar como transformei uma API comum em uma plataforma resiliente e auto‑mitigadora.”

---
## Slide 2 – O Problema
Contexto: APIs degradam em silêncio – latência cresce, erros intermitentes, diagnóstico lento.
Riscos: Perda de confiança, custo operacional, tempo de reação alto.
Tese: Visibilidade antecipada + mitigação automática reduz MTTR praticamente a zero.

---
## Slide 3 – Objetivos que Assumi
Explícitos: Catálogo funcional, organizado, observável.
Implícitos: Prevenção pró‑ativa, simplicidade operacional, facilidade de evolução.
Critério de sucesso: “Consigo explicar qualquer falha em < 1 min com dados.”

---
## Slide 4 – Arquitetura Macro
Hexagonal (Core isolado) + Adapters (HTTP / Repo in‑memory) + Observability Stack (Prometheus, Loki, Tempo, Grafana, Alertmanager) + Frontend leve.
Benefício: Domínio independente – fácil plugar DB, mensageria, cache.
Visual sugerido: (esboço rápido com camadas ou usar diagrama já pronto).

---
## Slide 5 – Fluxo de Uma Requisição
Cliente → Handler → Service → (Repo) → Resposta.
Telemetria paralela: Métricas + Trace + Log estruturado (correlacionado).
Mensagem: Cada request gera trilha completa para debugging determinístico.

---
## Slide 6 – Observabilidade 360°
Pilares: Métricas (RED/Golden), Traces (Tempo), Logs estruturados (Loki), Alertas (Alertmanager + WhatsApp).
Decisão: Priorizar campo `unix_ts` plano → consultas LogQL simples e rápidas.
Impacto: Redução do tempo cognitivo ao investigar.

---
## Slide 7 – Auto-Healing Preditivo
Mecanismo: Forecast leve + thresholds (latência P95 / erro %). Se projeção viola SLO → `/admin/mitigate`.
Logs distintos: `mitigation executed` (auto|manual) + `prediction cycle`.
Valor: MTTR virtual cai para segundos sem intervenção humana.

---
## Slide 8 – Design de Logs & Consultas
Formato plano JSON (sem nesting profundo). Campos: message, mode, unix_ts.
Consultas chave: `max_over_time(... unwrap unix_ts)` para última mitigação.
Resultado: Painéis de “Última Auto/Manual” e contagens confiáveis.

---
## Slide 9 – Qualidade & Confiabilidade
Testes: Handlers, serviço, repositório, middleware, logging, cobertura alvo de fluxos críticos.
Automação: Scripts de carga + simulação de degradação.
Decisão: Cobrir caminhos de mitigação antes de escalar features.

---
## Slide 10 – Segurança e Operabilidade
Admin token simples (ambiente demo) – já isolado logicamente.
Plano de evolução: JWT + RBAC + rate limiting + secrets externos.
Operação: Layout dashboard otimizado para tela pequena (menos ruído, foco em decisões).

---
## Slide 11 – Métricas de Impacto (Preparar Prints)
Exemplos (substituir com números coletados):
- P95 pré‑mitigação: ~4800ms → pós: ~120ms.
- Tempo médio até mitigação automática: < 30s.
- Ciclos de previsão em 1h: 120.
- Zero falhas após auto‑heal – tráfego estabilizado.
Mensagem: “Não é só teoria – medi efeito real.”

---
## Slide 12 – Demo (Roteiro)
1. Mostrar painel baseline.
2. Injetar latência (curl).
3. Ver latência subir + log de fault.
4. Aguardar ciclo → auto‑mitigação (log + queda de métricas).
5. Destacar timestamp atualizado.
Plano B: Mitigação manual (mesmos logs). Plano C: Explicar consultas.

---
## Slide 13 – Decisões & Trade-offs
Trade-offs conscientes: Sem DB inicial → foco em resiliência e telemetria.
Simplicidade de logs > Flexibilidade de formato aninhado.
Aceitei token simples para acelerar; documentei evolução.

---
## Slide 14 – Roadmap Futuro
Curto prazo: Persistência real (Postgres), autenticação, thresholds dinâmicos.
Médio: Circuit breaker inteligente, chaos injection controlada.
Longo: Recomendação preditiva baseada em padrões históricos (ML leve).

---
## Slide 15 – Alinhamento com a Empresa
Entrego: Velocidade + confiabilidade + capacidade de explicar o sistema.
Reduzo risco operacional e tempo de onboarding de novos devs.

---
## Slide 16 – O que me Diferencia
Mentalidade de produto (valor > feature), foco preventivo, documentação clara, decisões justificadas.

---
## Slide 17 – Fechamento & CTA
Mensagem final: “Conectei arquitetura limpa + observabilidade + ação preditiva para antecipar problemas. Quero aplicar esse mesmo rigor em escala aqui.”
CTA: Pronto para próximos desafios.

---
## Slide 18 – Q&A
Exemplos de perguntas (já preparado):
- Por que não microserviços? (Evolução incremental.)
- Como reduzir falsos positivos na previsão? (Janela + confirmação + suavização.)
- Migração para banco? (Adapter de repositório já isolado.)
- Segurança em produção? (JWT/RBAC/segredos externos/least privilege.)

---
## (Apêndice) Comandos de Demo
```bash
# Injetar latência
curl -X POST -H 'x-admin-token: secret' 'http://localhost:8000/admin/fault?mode=latency&inc=800'

# Injetar leak (se quiser mostrar)
curl -X POST -H 'x-admin-token: secret' 'http://localhost:8000/admin/fault?mode=leak&kb=50'

# Mitigar manualmente (fallback)
curl -X POST -H 'x-admin-token: secret' http://localhost:8000/admin/mitigate
```

---
## (Apêndice) Checklist Pré-Demo
- [ ] Grafana aberto (dashboard predictive-selfheal) – range 15m.
- [ ] API e monitor rodando (`docker compose ps`).
- [ ] Painel “Última Auto” com timestamp válido.
- [ ] Terminal com comandos já no histórico.
- [ ] Ajustar SLO_P95_MS se precisar acelerar trigger.
- [ ] Capturas de tela de backup salvas.

---
## (Apêndice) Narrativa Ultra-Resumida
Problema → Arquitetura limpa → Observabilidade completa → Auto-healing preditivo → Métricas de impacto → Roadmap → Alinhamento → CTA.

---
_Última atualização: 18/08/2025_
