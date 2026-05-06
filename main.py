import streamlit as st
import os
import json
import google.generativeai as genai

# Configuração da sua Chave que você enviou
GOOGLE_API_KEY = "AIzaSyCkCY0C6iehoiybkzrxAzvyh5aV9SwUKyE"
genai.configure(api_key=GOOGLE_API_KEY)

# Configuração do modelo (Gemini 1.5 Flash é rápido e bom)
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="Imperium IA - Humana", layout="wide")

class ImperiumHumano:
    def __init__(self):
        self.conhecimento = ""

    def carregar_aprendizado(self):
        dados_totais = []
        # Lê os JSONs dos fluxos
        if os.path.exists("fluxos_json"):
            for arq in os.listdir("fluxos_json"):
                if arq.endswith(".json"):
                    with open(f"fluxos_json/{arq}", 'r', encoding='utf-8') as f:
                        dados_totais.append(f.read())
        
        # Lê os Manuais em TXT
        if os.path.exists("base_conhecimento"):
            for arq in os.listdir("base_conhecimento"):
                if arq.endswith(".txt"):
                    with open(f"base_conhecimento/{arq}", 'r', encoding='utf-8') as f:
                        dados_totais.append(f.read())
        
        self.conhecimento = "\n".join(dados_totais)

# Inicializa o Bot
bot = ImperiumHumano()
bot.carregar_aprendizado()

st.title("🤖 Imperium Bot - Atendimento Inteligente")
st.caption("Agora converso de forma humana usando sua base de dados!")

# Histórico da conversa
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Campo de Chat
if prompt := st.chat_input("Como posso te ajudar?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Criamos a instrução de personalidade para a IA
        contexto_prompt = f"""
        Você é o assistente humano da Imperium TV. Seu nome é Imperium Bot.
        Você deve ser educado, prestativo e conversar de forma natural.
        
        Use as informações abaixo (que são seus manuais e fluxos) para responder ao cliente.
        Se não encontrar a informação, diga que vai encaminhar para o suporte humano.
        
        BASE DE CONHECIMENTO:
        {bot.conhecimento}
        
        PERGUNTA DO CLIENTE:
        {prompt}
        """
        
        try:
            response = model.generate_content(contexto_prompt)
            texto_resposta = response.text
            st.markdown(texto_resposta)
            st.session_state.messages.append({"role": "assistant", "content": texto_resposta})
        except Exception as e:
            st.error(f"Erro na IA: {e}")
