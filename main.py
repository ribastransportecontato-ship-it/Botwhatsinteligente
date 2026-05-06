import streamlit as st
import os
import json
import google.generativeai as genai

# Puxa a CHAVE NOVA que você configurou no Render
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Configura a IA com a nova chave
genai.configure(api_key=GOOGLE_API_KEY)

st.set_page_config(page_title="Imperium Bot - Gemini 2.5", layout="wide")

class ImperiumCerebro:
    def __init__(self):
        self.conhecimento_total = ""

    def carregar_arquivos(self):
        textos = []
        # Carrega os seus 48 arquivos JSON da pasta fluxos_json
        if os.path.exists("fluxos_json"):
            for arquivo in os.listdir("fluxos_json"):
                if arquivo.endswith(".json"):
                    try:
                        with open(f"fluxos_json/{arquivo}", 'r', encoding='utf-8') as f:
                            dados = json.load(f)
                            # Adiciona o nome do arquivo para o bot saber do que se trata
                            textos.append(f"ARQUIVO: {arquivo}\nCONTEÚDO: {json.dumps(dados, ensure_ascii=False)}")
                    except:
                        pass
        
        # Carrega Manuais TXT da pasta base_conhecimento
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

# Inicializa o carregamento dos arquivos
bot = iniciar_ia()

st.title("🤖 Imperium Bot (Gemini 2.5 Flash Lite)")

# Histórico de Chat
if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# Entrada do Usuário
if prompt := st.chat_input("Como posso ajudar a Imperium TV hoje?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # O modelo 2.5 Flash Lite tem espaço de sobra para seus arquivos
        instrucao = f"""
        Você é o assistente oficial da Imperium TV. 
        Responda de forma profissional e amigável.
        Use APENAS a base de conhecimento abaixo para suporte técnico.
        Se não souber, diga que encaminhará para um técnico humano.

        --- BASE DE DADOS ---
        {bot.conhecimento_total}
        """

        try:
            # USANDO O MODELO QUE APARECEU NO SEU GRÁFICO
            model = genai.GenerativeModel('gemini-2.5-flash-lite')
            
            # Gera a resposta
            response = model.generate_content([instrucao, prompt])
            
            resposta_texto = response.text
            st.markdown(resposta_texto)
            st.session_state.messages.append({"role": "assistant", "content": resposta_texto})
            
        except Exception as e:
            st.error(f"Erro na IA: {e}")
            st.info("Dica: Verifique se a nova API Key está correta no painel do Render.")

st.sidebar.success(f"Conectado ao Gemini 2.5!")
st.sidebar.write(f"Arquivos lidos: {len(bot.conhecimento_total.split('---'))}")
