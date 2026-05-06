from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# --- CONFIGURAÇÕES DAS SUAS CHAVES (Vistas nos prints) ---
APP_KEY = "f1e54647-cb4c-485e-af06-94837d5b2829"
AUTH_KEY = "wmRL7ay3DxrOpAJ6GfWGlQDP8HjOmUye8bfTagWI21kqVVli2U"
API_URL = "https://botbot.chat/api/v1/messages" # Verifique se este é o endpoint correto no manual da API do Botbot

def enviar_mensagem_botbot(numero, texto):
    """ Função para enviar a resposta de volta para o cliente via API do BotBot """
    payload = {
        "app_key": APP_KEY,
        "auth_key": AUTH_KEY,
        "to": numero,
        "message": texto
    }
    try:
        response = requests.post(API_URL, json=payload)
        return response.status_code
    except Exception as e:
        print(f"Erro ao enviar mensagem: {e}")
        return None

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    
    # Extrai a mensagem e o número do cliente (o formato depende do BotBot, ajuste se necessário)
    msg_cliente = data.get('message', '').lower()
    numero_cliente = data.get('from', '')

    if not msg_cliente or not numero_cliente:
        return jsonify({"status": "error", "message": "Dados incompletos"}), 400

    # --- REPERTÓRIO DE INTELIGÊNCIA IMPERIUM TV ---
    resposta = ""

    # 1. Suporte IB PLAYER PRO (DNS/Playlist)
    if "travando" in msg_cliente or "trava" in msg_cliente or "lento" in msg_cliente:
        if "ib" in msg_cliente or "ibo" in msg_cliente:
            resposta = (
                "🔄 *SUPORTE IB PLAYER PRO*\n\n"
                "Para resolver travamentos, siga este passo a passo:\n"
                "1️⃣ Vá no botão **CHANGE PLAYLIST** na tela inicial.\n"
                "2️⃣ Escolha um servidor diferente entre **IMPTV1 e IMPTV5**.\n"
                "3️⃣ Aguarde carregar. Isso troca a rota do DNS e estabiliza o sinal!"
            )
        # 2. Suporte NETPLAY (Sincronização)
        elif "netplay" in msg_cliente or "ntplay" in msg_cliente:
            resposta = (
                "🟢 *SUPORTE NETPLAY*\n\n"
                "Se as bolinhas estiverem vermelhas ou o canal não abrir:\n"
                "1️⃣ No canto inferior esquerdo, digite novamente seu **Usuário e Senha**.\n"
                "2️⃣ Clique em **ENTRAR**.\n"
                "Isso força a sincronização com o servidor e ativa o sinal (Bolinhas Verdes)!"
            )
        else:
            resposta = "🛠️ *CENTRAL DE SUPORTE*\n\nQual aplicativo você está usando? Digite *IB PLAYER* ou *NETPLAY* para eu te mandar o tutorial de correção de DNS."

    # 3. Instalação (Código Downloader)
    elif "instalar" in msg_cliente or "como baixar" in msg_cliente or "codigo" in msg_cliente:
        resposta = (
            "📺 *TUTORIAL DE INSTALAÇÃO*\n\n"
            "Para Android TV, TV Box ou Fire Stick:\n"
            "1️⃣ Baixe o app **Downloader** na loja de apps.\n"
            "2️⃣ Digite o código de acesso: **8454237**.\n"
            "3️⃣ O download do Netplay começará na hora!"
        )

    # 4. Financeiro e Renovação
    elif "pagar" in msg_cliente or "vencimento" in msg_cliente or "pix" in msg_cliente:
        resposta = (
            "💳 *FINANCEIRO IMPERIUM*\n\n"
            "Para renovar ou gerar seu PIX agora, acesse o painel oficial:\n"
            "🔗 https://botibo.onrender.com/\n\n"
            "Lembrando que os apps IB e Netplay têm uma taxa de licença anual de R$ 15,00."
        )

    # Se a IA identificou o assunto, envia a resposta técnica
    if resposta:
        enviar_mensagem_botbot(numero_cliente, resposta)
        return jsonify({"status": "success", "message": "Resposta enviada"}), 200
    
    return jsonify({"status": "ignored", "message": "Assunto não mapeado"}), 200

if __name__ == '__main__':
    # No Render, a porta é definida pela variável de ambiente PORT
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
