#!/usr/bin/env python3
"""
Teste simples de alertas - pode ser executado independentemente
"""

import requests
import json
from datetime import datetime

def test_webhook_local():
    """Testa webhook local sem Docker"""
    print("🧪 Testando sistema de alertas localmente...")
    
    # Simula payload do AlertManager
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
                "generatorURL": "http://prometheus:9090/graph?g0.expr=histogram_quantile%280.95%2C+sum%28rate%28http_request_duration_seconds_bucket%5B5m%5D%29%29+by+%28le%29%29+%3E+5&g0.tab=1",
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
    
    print("📤 Simulando alerta crítico de timeout...")
    print(f"📊 Payload: {json.dumps(alert_payload, indent=2)}")
    
    # Para teste, vamos apenas imprimir como seria o email/WhatsApp
    print("\n📧 EMAIL que seria enviado:")
    print("="*50)
    print(f"To: devops@yourcompany.com, oncall@yourcompany.com")
    print(f"Subject: 🚨 CRITICAL TIMEOUT ALERT - RequestTimeoutAlert")
    print(f"Body:")
    print(f"🚨 CRITICAL TIMEOUT ALERT")
    print(f"Summary: {alert_payload['alerts'][0]['annotations']['summary']}")
    print(f"Description: {alert_payload['alerts'][0]['annotations']['description']}")
    print(f"Severity: {alert_payload['alerts'][0]['labels']['severity']}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Runbook: {alert_payload['alerts'][0]['annotations']['runbook_url']}")
    
    print("\n📱 WHATSAPP que seria enviado:")
    print("="*50)
    whatsapp_message = f"""🚨 TIMEOUT ALERT 🚨

🎯 Service: Products API
📊 Alert: {alert_payload['alerts'][0]['annotations']['summary']}
📝 Description: {alert_payload['alerts'][0]['annotations']['description']}
⚡ Severity: {alert_payload['alerts'][0]['labels']['severity']}
🕒 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🔗 Dashboard: http://localhost:3000
📈 Grafana: Check traces section
🔍 Investigate immediately!"""
    
    print(whatsapp_message)
    
    return True

def simulate_timeout_scenario():
    """Simula um cenário que deve gerar o alerta"""
    print("\n🔥 Simulando cenário de timeout...")
    print("📈 Fazendo múltiplas requests para gerar latência...")
    
    import threading
    import time
    
    def make_request(req_id):
        try:
            start = time.time()
            response = requests.get('http://localhost:8000/v1/products', timeout=10)
            duration = time.time() - start
            if duration > 1:
                print(f"⏱️  Request {req_id}: {duration:.2f}s")
        except Exception as e:
            print(f"❌ Request {req_id}: {str(e)}")
    
    # Faz 30 requests simultâneas
    threads = []
    for i in range(30):
        thread = threading.Thread(target=make_request, args=(i,))
        threads.append(thread)
        thread.start()
    
    # Aguarda todas terminarem
    for thread in threads:
        thread.join()
    
    print("✅ Simulação completa!")
    print("🔍 Agora verifique:")
    print("   - Grafana: http://localhost:3000")
    print("   - Prometheus: http://localhost:9090/alerts")
    print("   - AlertManager: http://localhost:9093")

def check_prometheus_metrics():
    """Verifica métricas atuais no Prometheus"""
    print("\n📊 Verificando métricas do Prometheus...")
    
    try:
        # Query para P95 latency
        query = "histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[1m])) by (le))"
        url = f"http://localhost:9090/api/v1/query"
        params = {"query": query}
        
        response = requests.get(url, params=params, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                results = data.get('data', {}).get('result', [])
                if results:
                    value = float(results[0].get('value', [0, 0])[1])
                    print(f"📈 P95 Latency: {value:.3f}s")
                    
                    if value > 5:
                        print("🚨 ALERTA! Latência acima do limite de 5s")
                        return True
                    else:
                        print("✅ Latência dentro do limite")
                        return False
                else:
                    print("📊 Sem dados de latência disponíveis")
            else:
                print(f"❌ Erro no Prometheus: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Não foi possível conectar ao Prometheus")
        print("💡 Verifique se está rodando em http://localhost:9090")
    except Exception as e:
        print(f"❌ Erro inesperado: {str(e)}")
    
    return False

if __name__ == "__main__":
    print("🚀 SISTEMA DE ALERTAS DE TIMEOUT")
    print("=" * 40)
    
    print("\n1. 🧪 Teste do webhook de alertas")
    test_webhook_local()
    
    print("\n2. 📊 Verificação de métricas")
    timeout_detected = check_prometheus_metrics()
    
    if not timeout_detected:
        print("\n3. 🔥 Simulação de timeout")
        simulate_timeout_scenario()
        
        print("\n⏰ Aguardando 30s para métricas se propagarem...")
        import time
        time.sleep(30)
        
        print("\n4. 📊 Re-verificação após simulação")
        check_prometheus_metrics()
    
    print("\n✅ Teste completo!")
    print("\n📋 Próximos passos:")
    print("1. Configure credenciais reais no .env")
    print("2. Teste com Twilio/Gmail real")
    print("3. Configure números/emails de destino")
    print("4. Monitore alertas reais no ambiente de produção")
