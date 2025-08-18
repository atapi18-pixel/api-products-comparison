# Instruções de Execução

## 📋 Pré-requisito

**Único requisito: Docker instalado no sistema**

## 🚀 Como Rodar

Execute um único comando para iniciar toda a aplicação:

```bash
docker compose up -d --build
```

Isso iniciará automaticamente:

### 🎯 Serviços Principais
- **API Products**: http://localhost:8000
- **Dashboard Grafana**: http://localhost:3000/dashboards (admin/admin)

### 📊 Observabilidade
- **Prometheus**: http://localhost:9090
- **Loki**: http://localhost:3100
- **OpenTelemetry Collector**: Porta 4317

### 🧪 Testes Automatizados
- **K6 Load Tests**: Executam automaticamente a cada 10 minutos
- **Cenários incluem**: Requisições normais, erros 404, timeouts de 5s

### 🚨 Sistema de Alertas
- **WhatsApp**: Alertas automáticos para timeouts >5 segundos
- **Dashboard**: Monitoramento visual em tempo real

## 📱 Acessos Importantes

| Serviço | URL | Credenciais |
|---------|-----|-------------|
| API | http://localhost:8000 | - |
| Swagger Docs | http://localhost:8000/docs | - |
| Grafana Dashboard | http://localhost:3000 | admin/admin |
| Prometheus | http://localhost:9090 | - |

## 🧪 Testando a API

### Teste Rápido
```bash
curl "http://localhost:8000/v1/products?page=1&page_size=5"
```

### Teste de Timeout (Aciona Alertas)
```bash
curl -H "X-Delay: 5" "http://localhost:8000/v1/products"
```

## 📊 Monitoramento

Após a inicialização:
1. Acesse o dashboard em http://localhost:3000
2. Veja métricas em tempo real
3. Monitore os testes automatizados
4. Observe alertas de timeout no WhatsApp (configure as credenciais no docker-compose.yml)

## 🔧 Configuração de Alertas WhatsApp

Para receber alertas, edite as variáveis no `docker-compose.yml`:

```yaml
TWILIO_ACCOUNT_SID: your_account_sid
TWILIO_AUTH_TOKEN: your_auth_token
TWILIO_WHATSAPP_FROM: whatsapp:+14155238886
WHATSAPP_TO: whatsapp:+5511999999999
```

## 🛑 Parar os Serviços

```bash
docker compose down
```

---

**Tudo roda com Docker - nenhuma instalação local necessária!** 🐳

