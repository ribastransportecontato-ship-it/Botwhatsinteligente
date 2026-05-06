import streamlit as st
import os
import json
from groq import Groq

# Busca a chave nas variáveis de ambiente do Render
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

st.set_page_config(page_title="Imperium Bot - Central", layout="wide")

class ImperiumSistema:
    def __init__(self):
        self.base_conhecimento = ""

    def carregar_dados(self):
        conteudo_acumulado = []
        
        # Lendo os 48 arquivos de fluxo (JSON)
        if os.path.exists("fluxos_json"):
            arquivos = [f for f in os.listdir("fluxos_json") if f.endswith(".json")]
            for arquivo in arquivos:
                try:
                    with open(f"fluxos_json/{arquivo}", 'r', encoding='utf-8') as f:
                        dados = json.load(f)
                        # Pegamos as partes que realmente explicam algo (keywords e respostas)
                        # Isso economiza muito espaço para a IA
                        info_util = {
                            "tema": arquivo.replace(".json", ""),
                            "conteudo": dados.get("responses", dados) 
                        }
                        conteudo_acumulado.append(json.dumps(info_util, ensure_ascii=False))
                except:
                    pass
        
        # Lendo Manuais de Apoio (TXT)
        if os.path.exists("base_conhecimento"):
            for arquivo in os.listdir("base_conhecimento"):
                if arquivo.endswith(".txt"):
                    try:
                        with open(f"base_conhecimento/{arquivo}", 'r', encoding='utf-8') as f:
                            conteudo_acumulado.append(f.read())
                    except:
                        pass
        
        # Juntamos tudo. Com 48 arquivos, esse limite de 25k caracteres é seguro.
        self.base_conhecimento = "\n".join(conteudo_acumulado)[:25000]

@st.cache_resource
def preparar_bot():
    obj = ImperiumSistema()
    obj.carregar_dados()
    return obj

bot_motor = preparar_bot()

st.title("🤖 Imperium Bot - Atendimento")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if usuario_pergunta := st.chat_input("Como posso te ajudar?"):
    st.session_state.chat_history.append({"role": "user", "content": usuario_pergunta})
    with st.chat_message("user"):
        st.markdown(usuario_pergunta)

    with st.chat_message("assistant"):
        try:
            # Envia a pergunta com o contexto dos seus 48 arquivos
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system", 
                        "content": f"Você é o atendente da Imperium TV. Responda de forma humana e curta usando este guia: {bot_motor.base_conhecimento}"
                    },
                    {"role": "user", "content": usuario_pergunta}
                ],
                temperature=0.6,
                max_tokens=800
            )
            
            resposta_final = completion.choices[0].message.content
            st.markdown(resposta_final)
            st.session_state.chat_history.append({"role": "assistant", "content": resposta_final})
            
        except Exception as e:
            # Se o erro de tamanho persistir, ele avisa aqui
            st.error(f"Erro na conexão: {e}")

st.sidebar.write(f"📂 {len(os.listdir('fluxos_json')) if os.path.exists('fluxos_json') else 0} arquivos carregados.")
