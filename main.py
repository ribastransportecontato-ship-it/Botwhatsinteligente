import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# --- CONFIGURAÇÃO DE SEGURANÇA (Render) ---
APP_KEY = os.environ.get("BOTBOT_APP_KEY")
AUTH_KEY = os.environ.get("BOTBOT_AUTH_KEY")
# URL corrigida conforme a imagem da documentação (v2)
API_URL = "https://botbot.chat/api/v2/sendText"

def enviar_mensagem_botbot(numero, texto):
    if not APP_KEY or not AUTH_KEY:
        print("ERRO: Chaves não configuradas no Render!")
        return None

    # Conforme a documentação, as chaves vão nos HEADERS
    headers = {
        "appKey": APP_KEY,
        "authKey": AUTH_KEY,
        "Content-Type": "application/json"
    }

    # O corpo da mensagem conforme o exemplo da imagem
    payload = {
        "to": numero,
        "message": texto,
        "typingDelay": 1  # Simula digitação por 1 segundo
    }
    
    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=10)
        print(f"Tentativa para {numero} | Status: {response.status_code}")
        print(f"Resposta da API: {response.text}")
        return response.status_code
    except Exception as e:
        print(f"Erro na conexão: {e}")
        return None

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    
    # Captura a mensagem e o número de quem enviou
    msg_cliente = data.get('message', '').lower().strip()
    numero_cliente = data.get('from', '')

    if not msg_cliente or not numero_cliente:
        return jsonify({"status": "ignored"}), 200

    resposta = ""

    # Lógica de suporte (exemplo)
    if any(p in msg_cliente for p in ["travando", "lento", "parando"]):
        resposta = "🔄 *SUPORTE:* Se estiver no IB Player, tente mudar a Playlist em 'Change Playlist'. No Netplay, refaça o login no canto inferior esquerdo."
    
    elif any(p in msg_cliente for p in ["instalar", "baixar", "codigo"]):
        resposta = "📺 *INSTALAÇÃO:* Use o app Downloader com o código: *8454237*."

    # Execução do envio
    if resposta:
        enviar_mensagem_botbot(numero_cliente, resposta)
        return jsonify({"status": "success"}), 200
    
    return jsonify({"status": "no_keyword"}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
