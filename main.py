import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# --- CONFIGURAÇÃO ---
APP_KEY = os.environ.get("BOTBOT_APP_KEY")
AUTH_KEY = os.environ.get("BOTBOT_AUTH_KEY")
API_URL = "https://botbot.chat/api/v2/sendText"

# ⚠️ COLOQUE O NÚMERO DO SEU BOT AQUI PARA EVITAR LOOPS
MEU_NUMERO_BOT = "554488214771" 

def enviar_mensagem_botbot(numero, texto):
    if not APP_KEY or not AUTH_KEY:
        return None

    headers = {
        "appKey": APP_KEY,
        "authKey": AUTH_KEY,
        "Content-Type": "application/json"
    }

    numero_limpo = numero.split('@')[0]

    # TRAVA DE SEGURANÇA: Não envia mensagem para si mesmo
    if numero_limpo == MEU_NUMERO_BOT:
        print(f"Abortando: Tentativa de enviar mensagem para o próprio bot.")
        return None

    payload = {
        "to": numero_limpo,
        "message": texto,
        "typingDelay": 1
    }
    
    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=10)
        print(f"Envio para {numero_limpo} | Status: {response.status_code}")
        return response.status_code
    except Exception as e:
        print(f"Erro na conexão: {e}")
        return None

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if not data:
        return jsonify({"status": "no_data"}), 400
        
    msg_cliente = data.get('message', '').lower().strip()
    numero_raw = data.get('from', '')
    numero_cliente = numero_raw.split('@')[0]

    # --- TRAVA ANTI-LOOP ---
    # Se o número de quem enviou for o número do BOT, ignora totalmente.
    if numero_cliente == MEU_NUMERO_BOT:
        return jsonify({"status": "loop_prevented"}), 200

    resposta = ""

    # LÓGICA DE ATENDIMENTO
    if any(p in msg_cliente for p in ["travando", "lento", "trava"]):
        resposta = "🔄 *SUPORTE:* Se estiver no IB Player, mude a Playlist em 'Change Playlist'. No Netplay, refaça o login."
    
    elif any(p in msg_cliente for p in ["instalar", "baixar", "codigo"]):
        resposta = "📺 *INSTALAÇÃO:* No app Downloader, use o código: *8454237*."

    elif any(p in msg_cliente for p in ["oi", "olá", "ola", "bom dia"]):
        resposta = "🤖 *Olá! Sou o assistente da Imperium TV.*\nComo posso ajudar?\n1. *Travamento*\n2. *Instalar* o app"

    # Se tiver resposta e NÃO for o próprio bot, envia.
    if resposta:
        enviar_mensagem_botbot(numero_cliente, resposta)
        return jsonify({"status": "success"}), 200
    
    # Se não entendeu, só responde se for um humano (não o bot)
    # Para evitar loops, vamos desativar a resposta padrão por enquanto 
    # ou garantir que ela só saia para números diferentes do bot.
    return jsonify({"status": "ignored"}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
