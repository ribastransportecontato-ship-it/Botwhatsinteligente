import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# --- CONFIGURAÇÃO ---
APP_KEY = os.environ.get("BOTBOT_APP_KEY")
AUTH_KEY = os.environ.get("BOTBOT_AUTH_KEY")
API_URL = "https://botbot.chat/api/v2/sendText"

# COLOQUE O NÚMERO DO SEU BOT AQUI (O que está conectado no BotBot)
# Exemplo: "554488214771"
NUMERO_DO_BOT = "554488214771" 

@app.route('/', methods=['GET'])
def home():
    return "IMPERIUM TV - PROTEGIDO CONTRA LOOP", 200

def enviar(numero, texto):
    headers = {"appKey": APP_KEY, "authKey": AUTH_KEY, "Content-Type": "application/json"}
    payload = {"to": numero.split('@')[0], "message": texto}
    try:
        requests.post(API_URL, json=payload, headers=headers, timeout=10)
    except:
        pass

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if not data: return jsonify({"status": "ok"}), 200

    # Pega os dados da mensagem
    msg_recebida = str(data.get('message', '')).strip()
    msg = msg_recebida.lower()
    cliente_raw = str(data.get('from', ''))
    cliente = cliente_raw.split('@')[0]

    # --- TRAVA ANTI-LOOP ---
    # 1. Se o número que enviou for o mesmo número do Bot, IGNORA.
    if cliente == NUMERO_DO_BOT:
        print(f"--- LOOP DETECTADO: Mensagem do próprio bot ignorada ---")
        return jsonify({"status": "ignore_self"}), 200

    # 2. Se a mensagem for vazia ou sistema, IGNORA.
    if not msg or len(msg) < 1:
        return jsonify({"status": "ignore_empty"}), 200

    print(f"--- PROCESSANDO: {msg} de {cliente} ---")

    resposta = ""

    # LÓGICA HUMANIZADA
    if any(p in msg for p in ["oi", "olá", "ola", "bom dia", "boa tarde", "boa noite", "menu"]):
        resposta = (
            "Olá! Sou o assistente da *Imperium TV*. 🤖\n\n"
            "Para eu te ajudar rapidinho, o que você precisa?\n\n"
            "1️⃣ *Suporte* (Canais travando/fora)\n"
            "2️⃣ *Instalação* (Configurar app)\n"
            "3️⃣ *Renovação* (PIX/Valores)\n"
            "4️⃣ *Falar com Atendente*"
        )

    elif any(p in msg for p in ["1", "trava", "lento", "parou", "ib", "player"]):
        resposta = "Poxa, ninguém merece trava! 😟 Tente isso:\n\n1. Reinicie seu roteador (tire da tomada por 30s).\n2. No App, saia e entre na conta de novo.\n\nSe não voltar, digite *4* que eu te ajudo manualmente!"

    elif any(p in msg for p in ["2", "instala", "codigo", "código"]):
        resposta = "📺 *Instalação:* No app *Downloader*, use o código: *8454237*. Qualquer dúvida no passo a passo, é só chamar!"

    elif any(p in msg for p in ["3", "pagar", "pix", "valor", "renovar"]):
        resposta = "Perfeito! Me diga se prefere o plano Mensal ou o Trimestral (com desconto) que já te mando o PIX agora. 💳"

    elif msg == "4" or "atendente" in msg:
        resposta = "Entendido! Já avisei o Jefferson. ⏳ Aguarde um pouquinho que já vamos te responder aqui!"

    # RESPOSTA PADRÃO (Caso ele mande algo fora do menu)
    else:
        # Só responde se a mensagem não for muito pequena pra evitar loops de "kkk" ou emojis
        if len(msg) > 3:
            resposta = "Entendi! Você tentou reiniciar o modem e o app? Se precisar de algo específico, digite o número da opção ou aguarde o atendente."

    if resposta:
        enviar(cliente, resposta)

    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
