import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Configurações de Ambiente
APP_KEY = os.environ.get("BOTBOT_APP_KEY")
AUTH_KEY = os.environ.get("BOTBOT_AUTH_KEY")
API_URL = "https://botbot.chat/api/v2/sendText"

@app.route('/', methods=['GET'])
def home():
    return "IMPERIUM TV - ATENDIMENTO ATIVO", 200

def enviar(numero, texto):
    headers = {"appKey": APP_KEY, "authKey": AUTH_KEY, "Content-Type": "application/json"}
    payload = {"to": numero.split('@')[0], "message": texto}
    requests.post(API_URL, json=payload, headers=headers)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if not data: return jsonify({"status": "ok"}), 200

    msg = str(data.get('message', '')).lower().strip()
    cliente = data.get('from', '')

    # --- LÓGICA HUMANIZADA ---

    # 1. Saudação e Menu
    if any(p in msg for p in ["oi", "olá", "ola", "bom dia", "boa tarde", "boa noite", "menu"]):
        resposta = (
            "Olá! Eu sou o Assistente Virtual da *Imperium TV*. 🤖✨\n\n"
            "Estou aqui para garantir que seu atendimento seja feito com o máximo de rapidez! "
            "Me conte, o que está acontecendo ou o que você precisa fazer agora?\n\n"
            "👉 *1* - Suporte (Travamentos/Canais fora)\n"
            "👉 *2* - Instalação (Novos aparelhos)\n"
            "👉 *3* - Pagamentos / Renovação\n"
            "👉 *4* - Falar com um atendente"
        )

    # 2. Inteligência para Travamentos
    elif any(p in msg for p in ["1", "travando", "trava", "lento", "parou", "ib", "player"]):
        resposta = (
            "Poxa, ninguém merece travamento na hora do lazer! 😟\n\n"
            "Geralmente, 90% dos casos na Imperium TV se resolvem assim:\n\n"
            "✅ *Se usa IB Player:* Vá em Configurações e tente alternar a 'Playlist'.\n"
            "✅ *Se usa Netplay:* Saia do aplicativo e faça o login novamente.\n"
            "🌐 *Dica de Ouro:* Desligue seu roteador da tomada por 30 segundos e ligue de novo.\n\n"
            "Isso ajudou? Se não, digite *4* para falar com a gente!"
        )

    # 3. Inteligência para Instalação
    elif any(p in msg for p in ["2", "instalar", "instalação", "codigo", "código", "downloader"]):
        resposta = (
            "Certo! Vamos deixar tudo pronto para você assistir. 📺\n\n"
            "Se você estiver usando o app *Downloader*, basta digitar esse código:\n"
            "👉 *8454237*\n\n"
            "Ele vai baixar o nosso player oficial automaticamente. Precisa de ajuda com o passo a passo? É só avisar!"
        )

    # 4. Pagamentos
    elif any(p in msg for p in ["3", "pagar", "pix", "valor", "renovar", "vence"]):
        resposta = (
            "Quer garantir que seu sinal não caia? Perfeito! 💳\n\n"
            "Para agilizar, você prefere o plano mensal ou o promocional trimestral? "
            "Me avise que já te mando a chave PIX agora mesmo."
        )

    # 5. Atendente Humano
    elif msg == "4" or "atendente" in msg:
        resposta = "Entendido! Já chamei o pessoal aqui. ⏳ Em instantes um de nossos especialistas vai te dar continuidade no atendimento manual. Só um minutinho!"

    # 6. Resposta padrão para mensagens soltas (Ex: "uso o ib")
    else:
        resposta = (
            "Entendi! No caso do seu acesso, você tentou realizar aquele procedimento de reiniciar o modem e o aplicativo?\n\n"
            "Se precisar de algo específico, pode digitar o número da opção ou falar o que está acontecendo."
        )

    enviar(cliente, resposta)
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
