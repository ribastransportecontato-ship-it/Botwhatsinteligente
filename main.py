import streamlit as st
import os
import json
from google import genai # Nova biblioteca

# Configuração da sua Chave
GOOGLE_API_KEY = "AIzaSyCkCY0C6iehoiybkzrxAzvyh5aV9SwUKyE"
client = genai.Client(api_key=GOOGLE_API_KEY)

st.set_page_config(page_title="Imperium IA - Atendimento", layout="wide")

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

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Como posso te ajudar?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Instrução para a IA agir como humano usando sua base
        contexto_prompt = f"""
        Você é o assistente humano da Imperium TV. 
        Use as informações abaixo para responder ao cliente de forma amigável.
        
        BASE DE CONHECIMENTO:
        {bot.conhecimento}
        
        PERGUNTA DO CLIENTE:
        {prompt}
        """
        
        try:
            # Comando atualizado para a versão 2026 da API
            response = client.models.generate_content(
                model="gemini-1.5-flash", 
                contents=contexto_prompt
            )
            texto_resposta = response.text
            st.markdown(texto_resposta)
            st.session_state.messages.append({"role": "assistant", "content": texto_resposta})
        except Exception as e:
            st.error(f"Erro na IA: {e}")
