import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# --- CONFIGURAÇÃO ---
APP_KEY = os.environ.get("BOTBOT_APP_KEY")
AUTH_KEY = os.environ.get("BOTBOT_AUTH_KEY")
API_URL = "https://botbot.chat/api/v2/sendText"

# Deixamos vazio para o log nos dizer qual é o número real do bot
MEU_NUMERO_BOT = "554488214771" 

def enviar_mensagem_botbot(numero, texto):
    headers = {
        "appKey": APP_KEY,
        "authKey": AUTH_KEY,
        "Content-Type": "application/json"
    }
    payload = {"to": numero, "message": texto, "typingDelay": 1}
    
    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=10)
        print(f">>> RESPOSTA DA API: {response.status_code} - {response.text}")
        return response.status_code
    except Exception as e:
        print(f">>> ERRO AO ENVIAR: {e}")
        return None

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    print(f"--- NOVA MENSAGEM RECEBIDA ---")
    print(f"Dados: {data}") # Isso vai mostrar tudo que o BotBot envia
    
    if not data:
        return jsonify({"status": "no_data"}), 400
        
    msg_cliente = data.get('message', '').lower().strip()
    numero_raw = data.get('from', '')
    numero_cliente = numero_raw.split('@')[0]

    print(f"Mensagem: '{msg_cliente}' | De: {numero_cliente}")

    # Verifica se a mensagem veio do próprio bot
    if numero_cliente == MEU_NUMERO_BOT:
        print("Ignorado: É a própria mensagem do bot.")
        return jsonify({"status": "bot_self_ignore"}), 200

    resposta = ""
    if any(p in msg_cliente for p in ["oi", "olá", "ola", "bom dia"]):
        resposta = "🤖 Olá! Teste de recebimento ok. Como posso ajudar?"
    
    elif any(p in msg_cliente for p in ["travando", "lento", "trava"]):
        resposta = "🔄 Suporte: Tente mudar a playlist ou reiniciar o app."

    if resposta:
        print(f"Enviando resposta para {numero_cliente}...")
        enviar_mensagem_botbot(numero_cliente, resposta)
    else:
        print("Nenhuma palavra-chave identificada.")

    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
