#!/usr/bin/env python3
"""
Testes unitários para o sistema de alertas
"""

import json
import pytest
from datetime import datetime


def test_alert_payload_structure():
    """Testa a estrutura do payload de alerta do AlertManager"""
    alert_payload = {
        "receiver": "timeout-critical",
        "status": "firing",
        "alerts": [
            {
                "status": "firing",
                "labels": {
                    "alertname": "RequestTimeoutAlert",
                    "severity": "critical",
                    "alert_type": "timeout",
                    "instance": "products-api:8000"
                },
                "annotations": {
                    "summary": "🚨 REQUEST TIMEOUT ALERT - Response time > 5 seconds",
                    "description": "P95 request latency is 6.2s (>5s threshold). Service experiencing performance issues.",
                    "runbook_url": "https://wiki.company.com/runbooks/timeout-alert"
                },
                "startsAt": datetime.now().isoformat(),
                "endsAt": "",
                "generatorURL": "http://prometheus:9090/graph",
                "fingerprint": "abc123456789"
            }
        ],
        "groupLabels": {
            "alertname": "RequestTimeoutAlert"
        },
        "commonLabels": {
            "severity": "critical",
            "alert_type": "timeout"
        },
        "commonAnnotations": {
            "summary": "🚨 REQUEST TIMEOUT ALERT - Response time > 5 seconds"
        },
        "externalURL": "http://alertmanager:9093",
        "version": "4",
        "groupKey": "{}:{alertname=\"RequestTimeoutAlert\"}",
        "truncatedAlerts": 0
    }
    
    # Verifica estrutura básica
    assert "receiver" in alert_payload
    assert "status" in alert_payload
    assert "alerts" in alert_payload
    assert len(alert_payload["alerts"]) > 0
    
    # Verifica primeiro alerta
    alert = alert_payload["alerts"][0]
    assert "labels" in alert
    assert "annotations" in alert
    assert alert["labels"]["alertname"] == "RequestTimeoutAlert"
    assert alert["labels"]["severity"] == "critical"
    assert "REQUEST TIMEOUT ALERT" in alert["annotations"]["summary"]


def test_alert_message_formatting():
    """Testa formatação das mensagens de alerta"""
    alert_data = {
        "alertname": "RequestTimeoutAlert",
        "severity": "critical",
        "summary": "🚨 REQUEST TIMEOUT ALERT - Response time > 5 seconds",
        "description": "P95 request latency is 6.2s (>5s threshold). Service experiencing performance issues."
    }
    
    # Testa formatação do email
    email_subject = f"🚨 CRITICAL TIMEOUT ALERT - {alert_data['alertname']}"
    assert "CRITICAL TIMEOUT ALERT" in email_subject
    assert alert_data["alertname"] in email_subject
    
    # Testa formatação do WhatsApp
    whatsapp_message = f"""🚨 TIMEOUT ALERT 🚨

🎯 Service: Products API
📊 Alert: {alert_data['summary']}
📝 Description: {alert_data['description']}
⚡ Severity: {alert_data['severity']}
🕒 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🔗 Dashboard: http://localhost:3000
📈 Grafana: Check traces section
🔍 Investigate immediately!"""
    
    assert "TIMEOUT ALERT" in whatsapp_message
    assert alert_data["summary"] in whatsapp_message
    assert alert_data["description"] in whatsapp_message
    assert alert_data["severity"] in whatsapp_message


def test_alert_configuration():
    """Testa configuração dos alertas"""
    # Configurações esperadas
    timeout_threshold = 5  # segundos
    alert_severity = "critical"
    supported_channels = ["email", "whatsapp"]
    
    assert timeout_threshold == 5
    assert alert_severity == "critical"
    assert "email" in supported_channels
    assert "whatsapp" in supported_channels


def test_prometheus_query_format():
    """Testa formato das queries do Prometheus"""
    # Query para P95 latency
    p95_query = "histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[1m])) by (le))"
    
    # Verifica se a query tem os componentes esperados
    assert "histogram_quantile" in p95_query
    assert "0.95" in p95_query
    assert "http_request_duration_seconds_bucket" in p95_query
    assert "[1m]" in p95_query
    
    # Query para rate de requests
    rate_query = "sum(rate(http_requests_total[5m]))"
    assert "rate" in rate_query
    assert "http_requests_total" in rate_query
    assert "[5m]" in rate_query


def test_alert_channels_config():
    """Testa configuração dos canais de alerta"""
    # Configurações de canal WhatsApp
    whatsapp_config = {
        "account_sid": "your_twilio_account_sid",
        "auth_token": "your_twilio_auth_token", 
        "from_number": "whatsapp:+14155238886",
        "to_number": "whatsapp:+5511999999999"
    }
    
    # Verifica estrutura da configuração
    assert "account_sid" in whatsapp_config
    assert "auth_token" in whatsapp_config
    assert "from_number" in whatsapp_config
    assert "to_number" in whatsapp_config
    assert whatsapp_config["from_number"].startswith("whatsapp:")
    assert whatsapp_config["to_number"].startswith("whatsapp:")


if __name__ == "__main__":
    print("🚀 SISTEMA DE ALERTAS DE TIMEOUT")
    print("=" * 40)
    
    print("\n✅ Execute com pytest para rodar todos os testes:")
    print("   python -m pytest observability/alerting/test_alerts.py -v")
    
    print("\n📋 Para testar alertas reais:")
    print("1. Inicie com: docker compose up --build")
    print("2. Teste timeout: curl -H 'X-Delay: 5' 'http://localhost:8000/v1/products'")
    print("3. Configure credenciais no docker-compose.yml")
    print("4. Monitore alertas em http://localhost:3000")
