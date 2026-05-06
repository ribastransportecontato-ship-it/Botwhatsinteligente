import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# --- CONFIGURAÇÃO ---
APP_KEY = os.environ.get("BOTBOT_APP_KEY")
AUTH_KEY = os.environ.get("BOTBOT_AUTH_KEY")
API_URL = "https://botbot.chat/api/v2/sendText"

# Rota para o Render saber que o bot está online
@app.route('/', methods=['GET'])
def home():
    return "Bot Imperium TV Online!", 200

def enviar_mensagem(numero, texto):
    headers = {"appKey": APP_KEY, "authKey": AUTH_KEY, "Content-Type": "application/json"}
    numero_limpo = "".join(filter(str.isdigit, numero))
    
    payload = {"to": numero_limpo, "message": texto, "typingDelay": 0}
    try:
        r = requests.post(API_URL, json=payload, headers=headers, timeout=10)
        print(f"Status envio: {r.status_code}")
    except Exception as e:
        print(f"Erro envio: {e}")

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if not data: return jsonify({"status": "no_data"}), 200
        
    msg = data.get('message', '').lower().strip()
    cliente = data.get('from', '').split('@')[0]

    # Log para você ver no Render o que está chegando
    print(f"Recebido: {msg} de {cliente}")

    resposta = ""
    if msg in ["oi", "olá", "ola", "bom dia", "menu"]:
        resposta = "🤖 *Imperium TV*\n\nDigite o número da opção:\n*1* - Travamentos\n*2* - Instalação"
    elif msg == "1":
        resposta = "🔄 *SUPORTE:* Mude a Playlist no IB Player ou refaça o login no Netplay."
    elif msg == "2":
        resposta = "📺 *INSTALAÇÃO:* Código *8454237* no Downloader."

    if resposta:
        enviar_mensagem(cliente, resposta)
        
    return jsonify({"status": "processado"}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
