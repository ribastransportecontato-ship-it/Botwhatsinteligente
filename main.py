import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Pega as chaves que você configurou no Render (Environment Variables)
APP_KEY = os.environ.get("BOTBOT_APP_KEY")
AUTH_KEY = os.environ.get("BOTBOT_AUTH_KEY")
API_URL = "https://botbot.chat/api/v2/sendText"

@app.route('/', methods=['GET'])
def home():
    return "BOT IMPERIUM TV - ONLINE", 200

@app.route('/webhook', methods=['POST', 'GET']) # Aceita os dois para evitar erro 405
def webhook():
    # Se alguém tentar abrir no navegador
    if request.method == 'GET':
        return "Webhook aguardando dados...", 200

    data = request.get_json()
    print(f"--- DADOS RECEBIDOS DO BOTBOT: {data}")

    if not data:
        return jsonify({"status": "error", "message": "Sem dados"}), 200

    # Pega o texto e o número (removendo qualquer extra no final)
    msg = str(data.get('message', '')).lower().strip()
    cliente = str(data.get('from', '')).split('@')[0]

    resposta = ""
    
    # Lógica do Menu
    if any(p in msg for p in ["oi", "olá", "ola", "bom dia", "menu"]):
        resposta = "🤖 *Imperium TV*\n\n1 - Travamentos\n2 - Instalação\n3 - Falar com Humano"
    elif msg == "1":
        resposta = "🔄 *Suporte:* Reinicie seu modem e troque a Playlist no App."
    elif msg == "2":
        resposta = "📺 *Instalação:* Use o código *8454237* no Downloader."
    elif msg == "3":
        resposta = "⏳ Um atendente já vai te chamar!"

    if resposta:
        # Envio de volta para o BotBot
        headers = {
            "appKey": APP_KEY,
            "authKey": AUTH_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "to": cliente,
            "message": resposta
        }
        try:
            r = requests.post(API_URL, json=payload, headers=headers)
            print(f"--- STATUS DO ENVIO: {r.status_code} ---")
        except Exception as e:
            print(f"--- ERRO NO ENVIO: {e} ---")

    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
