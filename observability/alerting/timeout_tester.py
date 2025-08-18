#!/usr/bin/env python3
"""
Script para simular timeouts e testar alertas
Cria requests que demoram mais de 5 segundos para triggerar os alertas
"""

import time
import requests
import threading
from datetime import datetime

def simulate_slow_request():
    """Simula uma request lenta que vai triggar o alerta"""
    try:
        print(f"🐌 [{datetime.now().strftime('%H:%M:%S')}] Simulando request lenta...")
        
        # Primeira request normal
        start_time = time.time()
        response = requests.get('http://localhost:8000/v1/products', timeout=10)
        duration = time.time() - start_time
        
        print(f"✅ Request normal completada em {duration:.2f}s")
        
        # Agora vamos simular uma request que demora mais de 5 segundos
        # Como nossa API é rápida, vamos fazer múltiplas requests simultâneas
        # para sobrecarregar o sistema
        
        print("🔥 Iniciando sobrecarga do sistema...")
        threads = []
        
        for i in range(50):  # 50 requests simultâneas
            thread = threading.Thread(target=make_concurrent_request, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Aguarda todas as threads
        for thread in threads:
            thread.join()
            
        print("⏰ Aguardando alertas serem processados...")
        time.sleep(30)  # Aguarda 30s para os alertas serem processados
        
    except Exception as e:
        print(f"❌ Erro na simulação: {str(e)}")

def make_concurrent_request(request_id):
    """Faz uma request individual (para criar concorrência)"""
    try:
        start_time = time.time()
        response = requests.get('http://localhost:8000/v1/products', timeout=10)
        duration = time.time() - start_time
        
        if duration > 1:  # Log apenas requests mais lentas
            print(f"⏱️  Request {request_id}: {duration:.2f}s")
            
    except requests.exceptions.Timeout:
        print(f"⏰ Request {request_id}: TIMEOUT!")
    except Exception as e:
        print(f"❌ Request {request_id}: Erro - {str(e)}")

def simulate_timeout_scenario():
    """Cria um cenário real de timeout"""
    print("🎯 SIMULAÇÃO DE TIMEOUT INICIADA")
    print("=" * 50)
    
    # Cenário 1: Request burst para criar latência
    print("📈 Cenário 1: Request burst")
    simulate_slow_request()
    
    # Cenário 2: Verificar métricas no Prometheus
    print("\n📊 Cenário 2: Verificando métricas atuais")
    check_current_metrics()
    
    print("\n✅ Simulação completa!")
    print("🔍 Verifique:")
    print("   - Grafana Dashboard: http://localhost:3000")
    print("   - Prometheus Alerts: http://localhost:9090/alerts")
    print("   - AlertManager: http://localhost:9093")

def check_current_metrics():
    """Verifica as métricas atuais no Prometheus"""
    try:
        # Query para latência P95
        query = "histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[1m])) by (le))"
        url = f"http://localhost:9090/api/v1/query?query={query}"
        
        response = requests.get(url)
        data = response.json()
        
        if data.get('status') == 'success':
            results = data.get('data', {}).get('result', [])
            if results:
                value = float(results[0].get('value', [0, 0])[1])
                print(f"📊 P95 Latency atual: {value:.3f}s")
                if value > 5:
                    print("🚨 ALERTA: Latência acima de 5s!")
                else:
                    print("✅ Latência dentro do esperado")
            else:
                print("📊 Sem dados de latência disponíveis")
        else:
            print("❌ Erro ao consultar Prometheus")
            
    except Exception as e:
        print(f"❌ Erro ao verificar métricas: {str(e)}")

def test_alert_webhook():
    """Testa o webhook de alerta diretamente"""
    print("🧪 Testando webhook de alerta...")
    
    # Payload de teste simulando um alerta do AlertManager
    test_payload = {
        "alerts": [
            {
                "status": "firing",
                "labels": {
                    "alertname": "RequestTimeoutAlert",
                    "severity": "critical",
                    "alert_type": "timeout"
                },
                "annotations": {
                    "summary": "🚨 REQUEST TIMEOUT ALERT - Response time > 5 seconds",
                    "description": "P95 request latency is 6.5s (>5s threshold). Service may be experiencing performance issues."
                },
                "startsAt": datetime.now().isoformat(),
                "endsAt": "",
                "generatorURL": "http://prometheus:9090/graph"
            }
        ]
    }
    
    try:
        # Testa webhook crítico
        response = requests.post(
            'http://localhost:5000/webhook/whatsapp/critical',
            json=test_payload,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            print("✅ Webhook crítico testado com sucesso!")
        else:
            print(f"❌ Falha no webhook crítico: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro ao testar webhook: {str(e)}")

if __name__ == "__main__":
    print("🚀 TIMEOUT ALERT TESTER")
    print("=" * 30)
    print("Opções:")
    print("1. Simular cenário de timeout")
    print("2. Testar webhook diretamente")
    print("3. Verificar métricas atuais")
    
    choice = input("\nEscolha uma opção (1-3): ").strip()
    
    if choice == "1":
        simulate_timeout_scenario()
    elif choice == "2":
        test_alert_webhook()
    elif choice == "3":
        check_current_metrics()
    else:
        print("❌ Opção inválida")
