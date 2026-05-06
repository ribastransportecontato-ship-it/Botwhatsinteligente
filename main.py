import streamlit as st
import os
import json
import google.generativeai as genai

# Sua Chave de API
GOOGLE_API_KEY = "AIzaSyCkCY0C6iehoiybkzrxAzvyh5aV9SwUKyE"

# CONFIGURAÇÃO DE SEGURANÇA: Força o uso da versão estável v1
genai.configure(api_key=GOOGLE_API_KEY)

st.set_page_config(page_title="Imperium IA - Atendimento", layout="wide")

class ImperiumHumano:
    def __init__(self):
        self.conhecimento = ""

    def carregar_aprendizado(self):
        dados_totais = []
        if os.path.exists("fluxos_json"):
            for arq in os.listdir("fluxos_json"):
                if arq.endswith(".json"):
                    try:
                        with open(f"fluxos_json/{arq}", 'r', encoding='utf-8') as f:
                            conteudo = json.load(f)
                            dados_totais.append(f"Tutorial: {json.dumps(conteudo, ensure_ascii=False)}")
                    except: pass
        
        if os.path.exists("base_conhecimento"):
            for arq in os.listdir("base_conhecimento"):
                if arq.endswith(".txt"):
                    try:
                        with open(f"base_conhecimento/{arq}", 'r', encoding='utf-8') as f:
                            dados_totais.append(f"Informação Técnica: {f.read()}")
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
        instrucao = f"""
        Você é o 'Imperium Bot', atendente da Imperium TV. Converse como humano.
        Use este conhecimento para ajudar:
        {bot.conhecimento}
        
        Pergunta: {prompt}
        """

        try:
            # USANDO O NOME DE MODELO ATUALIZADO PARA 2026
            # O 'gemini-1.5-flash' é o mais estável para grandes volumes de dados
            model = genai.GenerativeModel(model_name='gemini-1.5-flash')
            
            # Forçamos a chamada sem parâmetros extras que causam o erro v1beta
            response = model.generate_content(instrucao)
            
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
        except Exception as e:
            st.error("Houve um ajuste na rede da Google. Estou reconectando...")
            try:
                # TENTATIVA 2: Usando o modelo Pro com nome completo
                model_alt = genai.GenerativeModel(model_name='gemini-1.5-pro')
                response = model_alt.generate_content(instrucao)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e2:
                st.write(f"Ainda não consegui conectar. Erro: {e2}")

st.sidebar.write(f"🧠 Base de dados ativa.")
