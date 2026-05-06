import streamlit as st
import os
import json
from google import genai

# Puxa a chave do Environment do Render
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# --- O PULO DO GATO ESTÁ AQUI ---
# Forçamos a API_VERSION para 'v1' para evitar o erro 404 da v1beta
client = genai.Client(
    api_key=GOOGLE_API_KEY,
    http_options={'api_version': 'v1'}
)

st.set_page_config(page_title="Imperium Bot - Gemini Stable", layout="wide")

class ImperiumCerebro:
    def __init__(self):
        self.conhecimento_total = ""

    def carregar_arquivos(self):
        textos = []
        if os.path.exists("fluxos_json"):
            for arquivo in os.listdir("fluxos_json"):
                if arquivo.endswith(".json"):
                    try:
                        with open(f"fluxos_json/{arquivo}", 'r', encoding='utf-8') as f:
                            dados = json.load(f)
                            textos.append(f"APP: {arquivo}\nCONTEUDO: {json.dumps(dados, ensure_ascii=False)}")
                    except: pass
        
        if os.path.exists("base_conhecimento"):
            for arquivo in os.listdir("base_conhecimento"):
                if arquivo.endswith(".txt"):
                    try:
                        with open(f"base_conhecimento/{arquivo}", 'r', encoding='utf-8') as f:
                            textos.append(f"MANUAL: {f.read()}")
                    except: pass
        
        self.conhecimento_total = "\n\n---\n\n".join(textos)

@st.cache_resource
def iniciar_ia():
    obj = ImperiumCerebro()
    obj.carregar_arquivos()
    return obj

bot = iniciar_ia()

st.title("🤖 Imperium Bot (Versão Estável 2026)")

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("Como posso ajudar?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        contexto_completo = f"""
        Você é o atendente da Imperium TV.
        Use este conhecimento para ajudar o cliente:
        {bot.conhecimento_total}
        
        Pergunta: {prompt}
        """

        try:
            # Chamada usando o modelo estável
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=contexto_completo
            )
            
            resposta_texto = response.text
            st.markdown(resposta_texto)
            st.session_state.messages.append({"role": "assistant", "content": resposta_texto})
            
        except Exception as e:
            st.error(f"Erro na IA: {e}")
