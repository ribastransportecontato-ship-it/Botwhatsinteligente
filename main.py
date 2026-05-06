import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# --- CONFIGURAÇÃO DE SEGURANÇA (Variáveis de Ambiente no Render) ---
# O código vai procurar estas chaves no painel 'Environment' do Render
APP_KEY = os.environ.get("BOTBOT_APP_KEY")
AUTH_KEY = os.environ.get("BOTBOT_AUTH_KEY")
API_URL = "https://botbot.chat/api/v1/messages"

def enviar_mensagem_botbot(numero, texto):
    """
    Envia a resposta técnica de volta para o cliente através da API do BotBot.
    """
    if not APP_KEY or not AUTH_KEY:
        print("ERRO: As chaves BOTBOT_APP_KEY ou BOTBOT_AUTH_KEY não foram configuradas no Render.")
        return None

    payload = {
        "app_key": APP_KEY,
        "auth_key": AUTH_KEY,
        "to": numero,
        "message": texto
    }
    
    try:
        # Envia a requisição POST para a API do BotBot
        response = requests.post(API_URL, json=payload, timeout=10)
        print(f"Status do envio para {numero}: {response.status_code}")
        return response.status_code
    except Exception as e:
        print(f"Erro ao conectar com a API do BotBot: {e}")
        return None

@app.route('/webhook', methods=['POST'])
def webhook():
    """
    Recebe as mensagens vindas do BotBot via Webhook.
    """
    data = request.get_json()
    
    # O BotBot envia os dados no corpo do JSON. 
    # Ajustamos para pegar a mensagem e o número do remetente.
    msg_cliente = data.get('message', '').lower().strip()
    numero_cliente = data.get('from', '')

    if not msg_cliente or not numero_cliente:
        return jsonify({"status": "error", "message": "Dados incompletos recebidos do Webhook"}), 400

    # --- LÓGICA DE ATENDIMENTO INTELIGENTE (REPERTÓRIO) ---
    resposta = ""

    # 1. Suporte para IB PLAYER PRO (Foco em Playlist/DNS)
    if any(palavra in msg_cliente for palavra in ["travando", "trava", "lento", "parando"]):
        if "ib" in msg_cliente or "ibo" in msg_cliente:
            resposta = (
                "🔄 *SUPORTE IB PLAYER PRO*\n\n"
                "Para resolver problemas de carregamento ou travamento:\n"
                "1️⃣ Clique no botão **CHANGE PLAYLIST** no menu inicial do App.\n"
                "2️⃣ Alterne para um servidor diferente (ex: de **IMPTV1** para **IMPTV3**).\n"
                "3️⃣ Isso mudará a rota do sinal e estabilizará a sua conexão!"
            )
        
        # 2. Suporte para NETPLAY (Foco em Sincronização)
        elif "netplay" in msg_cliente or "ntplay" in msg_cliente:
            resposta = (
                "🟢 *SUPORTE NETPLAY*\n\n"
                "Se os canais não abrirem ou as bolinhas estiverem vermelhas:\n"
                "1️⃣ Vá ao canto inferior esquerdo do ecrã.\n"
                "2️⃣ Digite novamente o seu **Usuário e Senha**.\n"
                "3️⃣ Clique em **ENTRAR**.\n"
                "Isso força a sincronização e ativa o sinal corretamente."
            )
        else:
            resposta = "🛠️ *CENTRAL DE SUPORTE*\n\nIdentifiquei que você está com dificuldades técnicas. Qual aplicação você utiliza: *IB PLAYER* ou *NETPLAY*?"

    # 3. Instalação e Códigos
    elif any(palavra in msg_cliente for palavra in ["instalar", "baixar", "codigo", "download"]):
        resposta = (
            "📺 *TUTORIAL DE INSTALAÇÃO*\n\n"
            "Para dispositivos Android TV, TV Box ou Fire Stick:\n"
            "1️⃣ Descarregue a aplicação **Downloader**.\n"
            "2️⃣ Introduza o código: **8454237**.\n"
            "3️⃣ O instalador do Netplay será iniciado automaticamente!"
        )

    # 4. Renovação e Pagamentos
    elif any(palavra in msg_cliente for palavra in ["pagar", "pix", "renovar", "vencimento"]):
        resposta = (
            "💳 *RENOVAÇÃO E PAGAMENTOS*\n\n"
            "Para gerar o seu código PIX e renovar o acesso agora, utilize o nosso painel:\n"
            "🔗 https://botibo.onrender.com/\n\n"
            "*Nota:* Aplicações como IB e Netplay possuem uma taxa de licença de R$ 15,00."
        )

    # --- EXECUÇÃO DO ENVIO ---
    if resposta:
        enviar_mensagem_botbot(numero_cliente, resposta)
        return jsonify({"status": "success", "topic": "mapped"}), 200
    
    # Caso o bot receba algo que não entende, você pode optar por não responder 
    # ou enviar um menu genérico. Aqui deixamos apenas o log.
    return jsonify({"status": "ignored", "topic": "unmapped"}), 200

if __name__ == '__main__':
    # Configuração de porta para o ambiente Render
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
