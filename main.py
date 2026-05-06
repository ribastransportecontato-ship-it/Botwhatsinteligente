import streamlit as st
import os
import json
from google import genai

# Puxa a chave do Environment do Render
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Inicializa o cliente
client = genai.Client(api_key=GOOGLE_API_KEY)

st.set_page_config(page_title="Imperium Bot - Final", layout="wide")

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
                            textos.append(f"APP: {arquivo}\nGUIA: {json.dumps(dados, ensure_ascii=False)}")
                    except: pass
        self.conhecimento_total = "\n\n---\n\n".join(textos)

@st.cache_resource
def iniciar_ia():
    obj = ImperiumCerebro()
    obj.carregar_arquivos()
    return obj

bot = iniciar_ia()

# --- FUNÇÃO PARA DESCOBRIR O NOME DO MODELO ---
def get_model_name():
    try:
        # Lista os modelos disponíveis na sua conta
        for m in client.models.list():
            if 'generateContent' in m.supported_methods and 'flash' in m.name:
                return m.name # Retorna o primeiro Flash que encontrar (ex: models/gemini-1.5-flash-002)
        return "gemini-1.5-flash" # Fallback
    except:
        return "gemini-1.5-flash"

st.title("🤖 Imperium Bot - Inteligência Ativa")

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
        try:
            # Descobre o nome que o Google quer usar hoje
            modelo_ativo = get_model_name()
            
            contexto_completo = f"""
            Você é o atendente da Imperium TV. Use este guia:
            {bot.conhecimento_total}
            
            Pergunta: {prompt}
            """

            response = client.models.generate_content(
                model=modelo_ativo,
                contents=contexto_completo
            )
            
            resposta_texto = response.text
            st.markdown(resposta_texto)
            st.session_state.messages.append({"role": "assistant", "content": resposta_texto})
            
        except Exception as e:
            st.error(f"Erro na IA: {e}")

st.sidebar.info(f"Modelo sendo usado: {get_model_name()}")
