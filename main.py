import streamlit as st
import os
import json
from groq import Groq

# Busca a chave nas variáveis de ambiente do Render (Seguro)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Inicializa o cliente da Groq
client = Groq(api_key=GROQ_API_KEY)

st.set_page_config(page_title="Imperium Bot - Central", layout="wide")

class ImperiumSistema:
    def __init__(self):
        self.base_conhecimento = ""

    def carregar_dados(self):
        conteudo_acumulado = []
        
        # Lendo os 111+ arquivos de fluxo (JSON)
        if os.path.exists("fluxos_json"):
            for arquivo in os.listdir("fluxos_json"):
                if arquivo.endswith(".json"):
                    try:
                        with open(f"fluxos_json/{arquivo}", 'r', encoding='utf-8') as f:
                            dados = json.load(f)
                            texto = f"Tutorial: {arquivo}. Conteúdo: {json.dumps(dados, ensure_ascii=False)}"
                            conteudo_acumulado.append(texto)
                    except:
                        pass
        
        # Lendo Manuais de Apoio (TXT)
        if os.path.exists("base_conhecimento"):
            for arquivo in os.listdir("base_conhecimento"):
                if arquivo.endswith(".txt"):
                    try:
                        with open(f"base_conhecimento/{arquivo}", 'r', encoding='utf-8') as f:
                            conteudo_acumulado.append(f"Manual Técnico: {f.read()}")
                    except:
                        pass
        
        self.base_conhecimento = "\n\n---\n\n".join(conteudo_acumulado)

# Inicia o motor do bot
@st.cache_resource
def preparar_bot():
    obj = ImperiumSistema()
    obj.carregar_dados()
    return obj

bot_motor = preparar_bot()

st.title("🤖 Imperium Bot - Atendimento Humano")
st.info("Sistema Inteligente alimentado por seus tutoriais do GitHub.")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if usuario_pergunta := st.chat_input("Como posso te ajudar agora?"):
    st.session_state.chat_history.append({"role": "user", "content": usuario_pergunta})
    with st.chat_message("user"):
        st.markdown(usuario_pergunta)

    with st.chat_message("assistant"):
        prompt_sistema = f"""
        Você é o Imperium Bot, um atendente humano da Imperium TV.
        Use a base abaixo para dar soluções técnicas. Fale de forma natural.
        
        BASE DE CONHECIMENTO:
        {bot_motor.base_conhecimento}
        """

        try:
            # ATUALIZADO: Usando o modelo Llama 3.1 (ou 3.3) que substituiu o 8b antigo
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant", # Modelo estável para 2026
                messages=[
                    {"role": "system", "content": "Você é um assistente prestativo."},
                    {"role": "user", "content": f"{prompt_sistema}\n\nPergunta: {usuario_pergunta}"}
                ],
                temperature=0.7,
            )
            
            resposta_final = completion.choices[0].message.content
            st.markdown(resposta_final)
            st.session_state.chat_history.append({"role": "assistant", "content": resposta_final})
            
        except Exception as e:
            st.error(f"Erro na conexão: {e}")

st.sidebar.title("Status")
st.sidebar.success("Cérebro carregado!")
