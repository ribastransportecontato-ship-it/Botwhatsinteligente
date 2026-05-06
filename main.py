import streamlit as st
import os
import json
import google.generativeai as genai

# Puxa a chave do Render (Verifique se não há espaços extras lá no painel!)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Configura a IA
genai.configure(api_key=GOOGLE_API_KEY)

st.set_page_config(page_title="Imperium Bot", layout="wide")

@st.cache_resource
def carregar_contexto():
    pasta = "fluxos_json"
    contexto = ""
    if os.path.exists(pasta):
        arquivos = [f for f in os.listdir(pasta) if f.endswith(".json")]
        for arq in arquivos[:48]: # Garante que lê seus 48 arquivos
            try:
                with open(os.path.join(pasta, arq), 'r', encoding='utf-8') as f:
                    conteudo = f.read()
                    contexto += f"\nGuia {arq}: {conteudo}"
            except:
                pass
    return contexto[:30000] # Limite de segurança para o modelo Flash

contexto_bot = carregar_contexto()

st.title("🤖 Imperium Bot")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Como posso ajudar?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # Usando o modelo generativo padrão
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Criando o prompt com as regras e a base
            prompt_completo = f"Você é o atendente da Imperium TV. Use a base: {contexto_bot}\n\nPergunta: {prompt}"
            
            response = model.generate_content(prompt_completo)
            
            resposta = response.text
            st.markdown(resposta)
            st.session_state.messages.append({"role": "assistant", "content": resposta})
            
        except Exception as e:
            st.error(f"Erro na IA: {e}")
            # Se der 404, o Streamlit vai nos mostrar o erro real aqui
