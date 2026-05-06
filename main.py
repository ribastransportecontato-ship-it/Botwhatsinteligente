import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# --- CONFIGURAÇÃO DE SEGURANÇA ---
# Estas chaves devem estar no painel 'Environment' do Render
APP_KEY = os.environ.get("BOTBOT_APP_KEY")
AUTH_KEY = os.environ.get("BOTBOT_AUTH_KEY")
API_URL = "https://botbot.chat/api/v2/sendText"

def enviar_mensagem_botbot(numero, texto):
    """ Envia a resposta técnica via API v2 do BotBot """
    if not APP_KEY or not AUTH_KEY:
        print("ERRO: Chaves não configuradas no Render!")
        return None

    headers = {
        "appKey": APP_KEY,
        "authKey": AUTH_KEY,
        "Content-Type": "application/json"
    }

    # Remove o @c.us caso o número venha formatado do WhatsApp
    numero_limpo = numero.split('@')[0]

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
    """ Recebe as mensagens do BotBot """
    data = request.get_json()
    if not data:
        return jsonify({"status": "no_data"}), 400
        
    msg_cliente = data.get('message', '').lower().strip()
    numero_cliente = data.get('from', '')

    if not msg_cliente or not numero_cliente:
        return jsonify({"status": "ignored"}), 200

    resposta = ""

    # --- LÓGICA DE ATENDIMENTO (PALAVRAS-CHAVE) ---
    if any(p in msg_cliente for p in ["travando", "lento", "trava", "parando"]):
        if "ib" in msg_cliente or "ibo" in msg_cliente:
            resposta = "🔄 *SUPORTE IB PLAYER:* Clique em 'Change Playlist' e alterne entre IMPTV1 e IMPTV5."
        elif "netplay" in msg_cliente:
            resposta = "🟢 *SUPORTE NETPLAY:* Reinsira o seu utilizador/palavra-passe no canto inferior e clique em ENTRAR."
        else:
            resposta = "🛠️ *SUPORTE:* Qual aplicação utiliza? *IB PLAYER* ou *NETPLAY*?"
    
    elif any(p in msg_cliente for p in ["instalar", "baixar", "codigo", "downloader"]):
        resposta = "📺 *INSTALAÇÃO:* No ecrã inicial da sua TV, abra a aplicação *Downloader* e use o código: *8454237*."

    elif any(p in msg_cliente for p in ["oi", "olá", "ola", "bom dia", "boa tarde"]):
        resposta = (
            "🤖 *Olá! Sou o assistente da Imperium TV.*\n\n"
            "Como posso ajudar?\n"
            "1. Suporte para *Travamento*\n"
            "2. Como *Instalar* o app\n"
            "3. Consultar *Vencimento*"
        )

    # --- RESPOSTA PADRÃO ---
    if not resposta:
        resposta = "🤔 Não entendi bem. Digite *Travando* para suporte ou *Instalar* para baixar o aplicativo."

    enviar_mensagem_botbot(numero_cliente, resposta)
    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    # Porta padrão para o Render
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
