import streamlit as st
import os
import json
from google import genai

# Sua Chave de API
GOOGLE_API_KEY = "AIzaSyCkCY0C6iehoiybkzrxAzvyh5aV9SwUKyE"

# Inicializa o cliente moderno (estável v1)
client = genai.Client(api_key=GOOGLE_API_KEY)

st.set_page_config(page_title="Imperium IA - Atendimento", layout="wide")

class ImperiumHumano:
    def __init__(self):
        self.conhecimento = ""

    def carregar_aprendizado(self):
        dados_totais = []
        # Carrega JSONs
        if os.path.exists("fluxos_json"):
            for arq in os.listdir("fluxos_json"):
                if arq.endswith(".json"):
                    try:
                        with open(f"fluxos_json/{arq}", 'r', encoding='utf-8') as f:
                            conteudo = json.load(f)
                            dados_totais.append(f"Fluxo {arq}: {json.dumps(conteudo, ensure_ascii=False)}")
                    except: pass
        
        # Carrega Manuais TXT
        if os.path.exists("base_conhecimento"):
            for arq in os.listdir("base_conhecimento"):
                if arq.endswith(".txt"):
                    try:
                        with open(f"base_conhecimento/{arq}", 'r', encoding='utf-8') as f:
                            dados_totais.append(f"Manual: {f.read()}")
                    except: pass
        
        self.conhecimento = "\n---\n".join(dados_totais)

@st.cache_resource
def iniciar_bot():
    bot = ImperiumHumano()
    bot.carregar_aprendizado()
    return bot

bot = iniciar_bot()

st.title("🤖 Imperium Bot - IA Humana")

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
        contexto_instrucao = f"""
        Você é o 'Imperium Bot', atendente da Imperium TV. Converse como um ser humano gentil.
        Use estritamente as informações abaixo para ajudar o cliente:
        
        {bot.conhecimento}
        
        Pergunta do cliente: {prompt}
        """

        try:
            # Usando a nova chamada da biblioteca google-genai
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=contexto_instrucao
            )
            
            texto_resposta = response.text
            st.markdown(texto_resposta)
            st.session_state.messages.append({"role": "assistant", "content": texto_resposta})
            
        except Exception as e:
            st.error(f"Erro de conexão com o cérebro da IA. Detalhe: {e}")
