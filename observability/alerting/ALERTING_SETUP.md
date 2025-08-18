# 🚨 SISTEMA DE ALERTAS DE TIMEOUT - GUIA COMPLETO

## 📋 **OVERVIEW**

Sistema completo de alertas que monitora requests com timeout acima de 5 segundos e envia notificações via:
- ✅ **Email** (SMTP/Gmail)
- ✅ **WhatsApp** (Twilio API)
- ✅ **Slack** (Webhook)

## 🎯 **ALERTAS CONFIGURADOS**

### 1. **RequestTimeoutAlert** (CRÍTICO)
- **Trigger**: P95 latency > 5 segundos por 1 minuto
- **Notificação**: Email + WhatsApp para equipe crítica
- **Severidade**: Critical

### 2. **SlowRequestAlert** (WARNING)
- **Trigger**: P99 latency > 5 segundos por 30 segundos  
- **Notificação**: Email para DevOps
- **Severidade**: Warning

### 3. **ExtremeLongRequest** (EMERGÊNCIA)
- **Trigger**: Qualquer request individual > 5 segundos
- **Notificação**: Email CTO + WhatsApp + Slack
- **Severidade**: Critical (imediato)

---

## ⚙️ **CONFIGURAÇÃO PASSO A PASSO**

### **Passo 1: Configurar Credenciais**

1. Copie o arquivo de exemplo:
```bash
cp observability/alerting/.env.example .env
```

2. **Configure Gmail/SMTP**:
   - Vá para https://myaccount.google.com/apppasswords
   - Crie uma "App Password" para o seu email
   - Configure no `.env`:
   ```env
   SMTP_USERNAME=seu-email@gmail.com
   SMTP_PASSWORD=sua-app-password-gerada
   ```

3. **Configure Twilio WhatsApp**:
   - Crie conta em https://console.twilio.com/
   - Configure WhatsApp Sandbox ou número verificado
   - Configure no `.env`:
   ```env
   TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxx
   TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxx
   WHATSAPP_TO_CRITICAL=whatsapp:+5511999999999
   ```

### **Passo 2: Iniciar Serviços**

```bash
# Rebuilda e inicia todos os serviços incluindo webhook
docker compose up -d --build
```

### **Passo 3: Verificar Configuração**

```bash
# Verifica se webhook está rodando
curl http://localhost:5000/health

# Testa envio de WhatsApp
curl -X POST http://localhost:5000/test/whatsapp
```

---

## 🧪 **TESTANDO OS ALERTAS**

### **Método 1: Script de Teste Automatizado**
```bash
cd observability/alerting
python timeout_tester.py
```

### **Método 2: Teste Manual de Sobrecarga**
```bash
# Gera múltiplas requests simultâneas para criar latência
for i in {1..100}; do 
  curl -s http://localhost:8000/v1/products > /dev/null &
done
wait
```

### **Método 3: Teste Direto do Webhook**
```bash
curl -X POST http://localhost:5000/webhook/whatsapp/critical \
  -H "Content-Type: application/json" \
  -d '{
    "alerts": [{
      "labels": {"alertname": "TEST", "severity": "critical"},
      "annotations": {"summary": "Teste de alerta"}
    }]
  }'
```

---

## 📊 **MONITORAMENTO DOS ALERTAS**

### **URLs de Monitoramento**
- **Prometheus Alerts**: http://localhost:9090/alerts
- **AlertManager**: http://localhost:9093
- **Grafana Dashboard**: http://localhost:3000
- **Webhook Health**: http://localhost:5000/health

### **Queries Úteis no Prometheus**
```promql
# Latência P95 atual
histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))

# Requests com timeout
increase(http_request_duration_seconds_bucket{le="5.0"}[5m])

# Alertas ativos
ALERTS{alertstate="firing"}
```

---

## 📱 **CONFIGURAÇÃO WHATSAPP DETALHADA**

### **Opção 1: Twilio Sandbox (Teste Gratuito)**
1. Acesse: https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn
2. Envie "join <seu-sandbox-code>" para +1 415 523 8886
3. Use `whatsapp:+14155238886` como FROM number

### **Opção 2: WhatsApp Business Verificado**
1. Configure número business na Twilio
2. Processo de verificação (pode levar alguns dias)
3. Use seu número verificado como FROM

### **Opção 3: Alternativas**
- **MessageBird**: API similar à Twilio
- **360dialog**: WhatsApp Business API
- **Meta WhatsApp Business API**: Diretamente com Meta

---

## 📧 **CONFIGURAÇÃO EMAIL AVANÇADA**

### **Templates Personalizados**
Os emails são enviados com HTML formatado:
- 🚨 **Critical**: Fundo vermelho, múltiplos destinatários
- ⚠️ **Warning**: Formato simples, apenas DevOps  
- 🔴 **Emergency**: Email para C-level + escalação

### **Configuração SMTP Personalizada**
```yaml
# No alertmanager/config.yml
global:
  smtp_smarthost: 'your-smtp-server:587'
  smtp_from: 'alerts@yourcompany.com'
  smtp_auth_username: 'your-username'
  smtp_auth_password: 'your-password'
```

---

## 🔧 **TROUBLESHOOTING**

### **Alertas não estão sendo enviados**
1. Verifique se Prometheus está coletando métricas:
   ```bash
   curl "http://localhost:9090/api/v1/query?query=up"
   ```

2. Verifique se AlertManager está ativo:
   ```bash
   curl http://localhost:9093/api/v1/alerts
   ```

3. Verifique logs do webhook:
   ```bash
   docker compose logs whatsapp-webhook
   ```

### **WhatsApp não está sendo enviado**
1. Verifique credenciais Twilio
2. Confirme número está no formato correto: `whatsapp:+5511999999999`
3. Para Sandbox, confirme que enviou "join" message

### **Emails não estão sendo enviados**
1. Verifique App Password do Gmail
2. Confirme 2FA está habilitado na conta Google
3. Teste SMTP connection manualmente

---

## 📈 **MÉTRICAS E DASHBOARDS**

### **Métricas Customizadas Adicionadas**
- `alert_notifications_sent_total`: Total de notificações enviadas
- `alert_webhook_requests_total`: Total de requests no webhook
- `alert_delivery_duration_seconds`: Tempo para entregar alerta

### **Dashboard de Alertas**
Acesse: http://localhost:3000/d/alerts/alerting-dashboard

Painéis incluem:
- Status dos alertas ativos
- Histórico de notificações  
- Latência de entrega
- Taxa de sucesso por canal

---

## 🚀 **PRÓXIMOS PASSOS**

### **Melhorias Recomendadas**
1. **PagerDuty Integration**: Para escalação automática
2. **Microsoft Teams**: Webhook para Teams
3. **SMS Alerts**: Via Twilio SMS para emergências
4. **Custom Webhooks**: Para sistemas internos
5. **Alert Fatigue Management**: Throttling inteligente

### **Monitoramento Avançado**
1. **SLI/SLO Alerts**: Service Level Indicators
2. **Anomaly Detection**: Machine learning para padrões
3. **Predictive Alerts**: Alertas baseados em tendências
4. **Multi-region**: Alertas distribuídos

---

## 📞 **SUPORTE**

Em caso de problemas:
1. Verifique logs: `docker compose logs -f`
2. Teste conectividade: Scripts em `alerting/`
3. Valide configurações: URLs de health check
4. Consulte documentação oficial das APIs

---

*Sistema de Alertas v1.0 - Configurado em {{ date }}*
