import streamlit as st
import os
import json
from groq import Groq

# Busca a chave nas variáveis de ambiente do Render
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

st.set_page_config(page_title="Imperium Bot", layout="wide")

class ImperiumSistema:
    def __init__(self):
        self.lista_temas = ""

    def carregar_dados(self):
        temas = []
        if os.path.exists("fluxos_json"):
            arquivos = [f for f in os.listdir("fluxos_json") if f.endswith(".json")]
            for arquivo in arquivos:
                # Mandamos apenas o nome do arquivo para a IA saber que o manual existe
                nome_limpo = arquivo.replace(".json", "").replace("_", " ")
                temas.append(nome_limpo)
        
        # Criamos um índice curto em vez de mandar o texto todo
        self.lista_temas = ", ".join(temas)

@st.cache_resource
def preparar_bot():
    obj = ImperiumSistema()
    obj.carregar_dados()
    return obj

bot_motor = preparar_bot()

st.title("🤖 Imperium Bot")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if usuario_pergunta := st.chat_input("Como posso ajudar?"):
    st.session_state.chat_history.append({"role": "user", "content": usuario_pergunta})
    with st.chat_message("user"):
        st.markdown(usuario_pergunta)

    with st.chat_message("assistant"):
        try:
            # Mandamos apenas a lista de manuais disponíveis
            prompt_curto = f"""Você é o atendente da Imperium TV. 
            Você tem manuais sobre: {bot_motor.lista_temas}.
            Responda de forma humana. Se o cliente pedir um tutorial, tente explicar baseado no nome do tema ou peça para ele ser específico."""

            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": prompt_curto},
                    {"role": "user", "content": usuario_pergunta}
                ],
                temperature=0.7,
            )
            
            resposta_final = completion.choices[0].message.content
            st.markdown(resposta_final)
            st.session_state.chat_history.append({"role": "assistant", "content": resposta_final})
            
        except Exception as e:
            st.error(f"Erro: {e}")
