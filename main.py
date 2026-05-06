import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# --- CONFIGURAÇÃO ---
APP_KEY = os.environ.get("BOTBOT_APP_KEY")
AUTH_KEY = os.environ.get("BOTBOT_AUTH_KEY")
API_URL = "https://botbot.chat/api/v2/sendText"

def enviar_mensagem(numero, texto):
    headers = {"appKey": APP_KEY, "authKey": AUTH_KEY, "Content-Type": "application/json"}
    # Limpeza total do número para evitar erros de formato
    numero_limpo = "".join(filter(str.isdigit, numero))
    
    payload = {"to": numero_limpo, "message": texto, "typingDelay": 0}
    try:
        requests.post(API_URL, json=payload, headers=headers, timeout=10)
    except:
        pass

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if not data: return jsonify({"status": "error"}), 400
        
    # Pega o texto e quem enviou
    msg = data.get('message', '').lower().strip()
    cliente = data.get('from', '').split('@')[0]

    # --- LÓGICA DE RESPOSTA RESTRITA (EVITA LOOP) ---
    # O Bot SÓ responde se a mensagem for uma dessas palavras EXATAS.
    # Se ele receber a própria mensagem (que é longa), ele não responde.
    
    resposta = ""
    
    if msg in ["oi", "olá", "ola", "bom dia", "menu"]:
        resposta = "🤖 *Imperium TV*\n\nDigite a opção:\n*1* - Travamentos\n*2* - Instalação"
        
    elif msg == "1":
        resposta = "🔄 *SUPORTE:* Se usa IB Player, mude a Playlist. No Netplay, refaça o login."
        
    elif msg == "2":
        resposta = "📺 *INSTALAÇÃO:* Use o código *8454237* no app Downloader."

    if resposta:
        enviar_mensagem(cliente, resposta)
        return jsonify({"status": "enviado"}), 200
    
    return jsonify({"status": "ignorado_para_evitar_loop"}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
