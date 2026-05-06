import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# --- CONFIGURAÇÃO ---
APP_KEY = os.environ.get("BOTBOT_APP_KEY")
AUTH_KEY = os.environ.get("BOTBOT_AUTH_KEY")
API_URL = "https://botbot.chat/api/v2/sendText"

@app.route('/', methods=['GET'])
def home():
    return "SERVIDOR ATIVO - IMPERIUM TV", 200

def enviar_mensagem(numero, texto):
    headers = {"appKey": APP_KEY, "authKey": AUTH_KEY, "Content-Type": "application/json"}
    numero_limpo = "".join(filter(str.isdigit, numero))
    payload = {"to": numero_limpo, "message": texto, "typingDelay": 0}
    try:
        r = requests.post(API_URL, json=payload, headers=headers, timeout=10)
        print(f"==> ENVIO PARA {numero_limpo}: Status {r.status_code}")
    except Exception as e:
        print(f"==> ERRO NO ENVIO: {e}")

@app.route('/webhook', methods=['POST'])
def webhook():
    # Log imediato para saber se algo entrou
    print("!!! MENSAGEM DETECTADA NO WEBHOOK !!!")
    
    data = request.get_json()
    if not data:
        print("Dados recebidos vazios ou inválidos.")
        return jsonify({"status": "no_data"}), 200
        
    print(f"Conteúdo Bruto: {data}")

    msg = str(data.get('message', '')).lower().strip()
    cliente = str(data.get('from', '')).split('@')[0]

    resposta = ""
    if any(p in msg for p in ["oi", "olá", "ola", "bom dia", "menu"]):
        resposta = "🤖 *Imperium TV*\n\nEscolha uma opção:\n1. Suporte Travamentos\n2. Instalação"
    elif msg == "1":
        resposta = "🔄 *SUPORTE:* Mude a Playlist ou refaça o login no App."
    elif msg == "2":
        resposta = "📺 *INSTALAÇÃO:* Use o código *8454237* no Downloader."

    if resposta:
        enviar_mensagem(cliente, resposta)
    
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
