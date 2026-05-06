import streamlit as st
import os
import json
import google.generativeai as genai

# Puxa a chave do Render (Seguro)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Configura o Gemini para usar a versão estável v1
genai.configure(api_key=GOOGLE_API_KEY)

st.set_page_config(page_title="Imperium Bot - Gemini", layout="wide")

class ImperiumCerebro:
    def __init__(self):
        self.conhecimento_total = ""

    def carregar_arquivos(self):
        textos = []
        # Carrega os 48 arquivos JSON
        if os.path.exists("fluxos_json"):
            for arquivo in os.listdir("fluxos_json"):
                if arquivo.endswith(".json"):
                    try:
                        with open(f"fluxos_json/{arquivo}", 'r', encoding='utf-8') as f:
                            dados = json.load(f)
                            textos.append(f"ARQUIVO: {arquivo}\nCONTEÚDO: {json.dumps(dados, ensure_ascii=False)}")
                    except:
                        pass
        
        # Carrega Manuais TXT
        if os.path.exists("base_conhecimento"):
            for arquivo in os.listdir("base_conhecimento"):
                if arquivo.endswith(".txt"):
                    try:
                        with open(f"base_conhecimento/{arquivo}", 'r', encoding='utf-8') as f:
                            textos.append(f"MANUAL: {f.read()}")
                    except:
                        pass
        
        self.conhecimento_total = "\n\n---\n\n".join(textos)

@st.cache_resource
def iniciar_ia():
    obj = ImperiumCerebro()
    obj.carregar_arquivos()
    return obj

bot = iniciar_ia()

st.title("🤖 Imperium Bot (Gemini 1.5 Flash)")

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("Como posso te ajudar?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # O Gemini 1.5 aguenta esse volume de texto tranquilamente
        instrucao = f"""
        Você é o atendente humano da Imperium TV. 
        Seu tom deve ser amigável, prestativo e claro.
        
        Use as informações abaixo para responder tecnicamente ao cliente.
        Se a informação não estiver na base, diga que vai verificar com o suporte.
        
        BASE DE CONHECIMENTO COMPLETA:
        {bot.conhecimento_total}
        """

        try:
            # Forçamos o modelo 1.5 Flash
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Criamos o chat com o contexto
            response = model.generate_content([instrucao, prompt])
            
            resposta_texto = response.text
            st.markdown(resposta_texto)
            st.session_state.messages.append({"role": "assistant", "content": resposta_texto})
            
        except Exception as e:
            st.error(f"Erro no Gemini: {e}")

st.sidebar.success(f"Cérebro ativo com os arquivos do GitHub!")
