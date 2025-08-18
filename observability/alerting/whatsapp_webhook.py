#!/usr/bin/env python3
"""
WhatsApp Webhook Server para Alertas de Timeout
Simula envio de mensagens via WhatsApp API (Twilio/MessageBird)
"""

from flask import Flask, request, jsonify
import json
import requests
import os
from datetime import datetime

app = Flask(__name__)

# Configurações - substitua pelos seus dados reais
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', 'your-account-sid')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', 'your-auth-token')
TWILIO_WHATSAPP_FROM = os.getenv('TWILIO_WHATSAPP_FROM', 'whatsapp:+14155238886')  # Twilio Sandbox
WHATSAPP_TO_CRITICAL = os.getenv('WHATSAPP_TO_CRITICAL', 'whatsapp:+5511999999999')  # Seu número
WHATSAPP_TO_EMERGENCY = os.getenv('WHATSAPP_TO_EMERGENCY', 'whatsapp:+5511888888888')  # Número emergência

def send_whatsapp_message(to_number, message):
    """Envia mensagem via Twilio WhatsApp API"""
    try:
        url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Messages.json"
        
        data = {
            'From': TWILIO_WHATSAPP_FROM,
            'To': to_number,
            'Body': message
        }
        
        response = requests.post(
            url,
            auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN),
            data=data
        )
        
        if response.status_code == 201:
            print(f"✅ WhatsApp enviado para {to_number}")
            return True
        else:
            print(f"❌ Erro ao enviar WhatsApp: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exceção ao enviar WhatsApp: {str(e)}")
        return False

def format_alert_message(alert_data, alert_type="critical"):
    """Formata mensagem de alerta"""
    alerts = alert_data.get('alerts', [])
    
    if not alerts:
        return "⚠️ Alerta recebido sem detalhes"
    
    alert = alerts[0]  # Pega o primeiro alerta
    
    emoji = "🚨" if alert_type == "critical" else "🔴" if alert_type == "emergency" else "⚠️"
    
    message = f"""{emoji} TIMEOUT ALERT {emoji}

🎯 Service: Products API
📊 Alert: {alert.get('annotations', {}).get('summary', 'Timeout detected')}
📝 Description: {alert.get('annotations', {}).get('description', 'Request taking too long')}
⚡ Severity: {alert.get('labels', {}).get('severity', 'unknown')}
🕒 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🔗 Dashboard: http://localhost:3000
📈 Grafana: Check traces section
🔍 Investigate immediately!"""

    return message

@app.route('/webhook/whatsapp/critical', methods=['POST'])
def whatsapp_critical():
    """Webhook para alertas críticos de timeout"""
    try:
        alert_data = request.get_json()
        print(f"📥 Recebido alerta crítico: {json.dumps(alert_data, indent=2)}")
        
        message = format_alert_message(alert_data, "critical")
        success = send_whatsapp_message(WHATSAPP_TO_CRITICAL, message)
        
        return jsonify({
            'status': 'success' if success else 'error',
            'message': 'WhatsApp crítico enviado' if success else 'Falha no envio',
            'alert_type': 'critical'
        }), 200 if success else 500
        
    except Exception as e:
        print(f"❌ Erro no webhook crítico: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/webhook/whatsapp/emergency', methods=['POST'])
def whatsapp_emergency():
    """Webhook para alertas de emergência"""
    try:
        alert_data = request.get_json()
        print(f"🔴 Recebido alerta de EMERGÊNCIA: {json.dumps(alert_data, indent=2)}")
        
        message = format_alert_message(alert_data, "emergency")
        
        # Envia para múltiplos números em emergência
        success_critical = send_whatsapp_message(WHATSAPP_TO_CRITICAL, message)
        success_emergency = send_whatsapp_message(WHATSAPP_TO_EMERGENCY, message)
        
        return jsonify({
            'status': 'success' if (success_critical or success_emergency) else 'error',
            'message': 'WhatsApp emergência enviado',
            'alert_type': 'emergency',
            'sent_to': {
                'critical': success_critical,
                'emergency': success_emergency
            }
        }), 200
        
    except Exception as e:
        print(f"❌ Erro no webhook emergência: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check do webhook server"""
    return jsonify({
        'status': 'healthy',
        'service': 'whatsapp-webhook',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/test/whatsapp', methods=['POST'])
def test_whatsapp():
    """Endpoint para testar envio de WhatsApp"""
    try:
        test_message = """🧪 TESTE DE ALERTA

Este é um teste do sistema de alertas de timeout.
Se você recebeu esta mensagem, o sistema está funcionando!

🕒 """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        success = send_whatsapp_message(WHATSAPP_TO_CRITICAL, test_message)
        
        return jsonify({
            'status': 'success' if success else 'error',
            'message': 'Teste enviado' if success else 'Falha no teste'
        }), 200 if success else 500
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Iniciando WhatsApp Webhook Server...")
    print("📱 Endpoints disponíveis:")
    print("   - POST /webhook/whatsapp/critical")
    print("   - POST /webhook/whatsapp/emergency") 
    print("   - GET  /health")
    print("   - POST /test/whatsapp")
    print()
    print("⚙️ Configuração:")
    print(f"   - Twilio SID: {TWILIO_ACCOUNT_SID[:10]}...")
    print(f"   - WhatsApp From: {TWILIO_WHATSAPP_FROM}")
    print(f"   - WhatsApp To (Critical): {WHATSAPP_TO_CRITICAL}")
    print(f"   - WhatsApp To (Emergency): {WHATSAPP_TO_EMERGENCY}")
    print()
    
    app.run(host='0.0.0.0', port=5000, debug=True)
