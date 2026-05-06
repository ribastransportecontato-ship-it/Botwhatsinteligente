import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# --- CONFIGURAÇÃO (Variáveis de Ambiente no Render) ---
APP_KEY = os.environ.get("BOTBOT_APP_KEY")
AUTH_KEY = os.environ.get("BOTBOT_AUTH_KEY")
API_URL = "https://botbot.chat/api/v2/sendText"

# Rota para o Render saber que o serviço está vivo
@app.route('/', methods=['GET'])
def home():
    return "SERVIDOR IMPERIUM TV ATIVO", 200

def enviar_mensagem(numero, texto):
    headers = {
        "appKey": APP_KEY, 
        "authKey": AUTH_KEY, 
        "Content-Type": "application/json"
    }
    
    # Limpa o número e garante o prefixo 55 (Brasil)
    numero_limpo = "".join(filter(str.isdigit, numero))
    if not numero_limpo.startswith("55"):
        numero_limpo = "55" + numero_limpo

    payload = {
        "to": numero_limpo, 
        "message": texto, 
        "typingDelay": 0
    }
    
    try:
        r = requests.post(API_URL, json=payload, headers=headers, timeout=15)
        print(f"==> LOG DE ENVIO PARA {numero_limpo}:")
        print(f"==> STATUS API: {r.status_code}")
        print(f"==> RESPOSTA API: {r.text}") # Isso aqui vai nos dizer o erro real se não chegar
        return r.status_code
    except Exception as e:
        print(f"==> ERRO CRÍTICO NA REQUISIÇÃO: {e}")
        return None

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    
    if not data:
        return jsonify({"status": "error", "message": "No data received"}), 200
    
    # Extrai mensagem e número
    msg = str(data.get('message', '')).lower().strip()
    cliente_raw = str(data.get('from', ''))
    # Remove qualquer sufixo como @s.whatsapp.net se houver
    cliente = cliente_raw.split('@')[0]

    print(f"--- NOVA MENSAGEM: '{msg}' DE: {cliente} ---")

    resposta = ""

    # MENU PRINCIPAL
    if any(p in msg for p in ["oi", "olá", "ola", "bom dia", "menu"]):
        resposta = (
            "🤖 *Imperium TV - Atendimento Automático*\n\n"
            "Como posso te ajudar hoje? Digite o número:\n\n"
            "*1* - Suporte com Travamentos\n"
            "*2* - Instalação de Aplicativos\n"
            "*3* - Falar com atendente"
        )
    
    # OPÇÃO 1 - SUPORTE
    elif msg == "1":
        resposta = (
            "🔄 *DICA PARA TRAVAMENTOS:*\n\n"
            "1. Se usa o *IB Player*, tente trocar a Playlist nas configurações.\n"
            "2. No *Netplay*, saia e faça o login novamente.\n"
            "3. Reinicie seu roteador por 30 segundos."
        )

    # OPÇÃO 2 - INSTALAÇÃO
    elif msg == "2":
        resposta = (
            "📺 *PARA INSTALAR:*\n\n"
            "Abra o app *Downloader* e use o código abaixo:\n"
            "👉 *8454237*\n\n"
            "Depois é só seguir a instalação padrão."
        )

    # OPÇÃO 3 - ATENDENTE
    elif msg == "3":
        resposta = "⏳ Aguarde um momento. Um atendente humano irá te responder em breve!"

    # EXECUÇÃO DO ENVIO
    if resposta:
        enviar_mensagem(cliente, resposta)
    else:
        print(f"Mensagem '{msg}' ignorada (fora do menu).")

    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    # O Render define a porta automaticamente
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
