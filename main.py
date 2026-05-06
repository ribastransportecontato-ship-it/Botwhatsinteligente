import streamlit as st
import os
import json
import google.generativeai as genai
import time

# Puxa a chave do Render
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Configura a IA
genai.configure(api_key=GOOGLE_API_KEY)

st.set_page_config(page_title="Imperium Bot - Suporte", layout="wide")

class ImperiumCerebro:
    def __init__(self):
        self.conhecimento_total = ""

    def carregar_arquivos(self):
        textos = []
        # Carrega arquivos da pasta fluxos_json
        if os.path.exists("fluxos_json"):
            for arquivo in os.listdir("fluxos_json"):
                if arquivo.endswith(".json"):
                    try:
                        with open(f"fluxos_json/{arquivo}", 'r', encoding='utf-8') as f:
                            dados = json.load(f)
                            # Pegamos os primeiros 2000 caracteres de cada JSON para economizar cota
                            conteudo_resumido = json.dumps(dados, ensure_ascii=False)[:2000]
                            textos.append(f"APP: {arquivo} | GUIA: {conteudo_resumido}")
                    except: pass
        
        # Carrega Manuais TXT
        if os.path.exists("base_conhecimento"):
            for arquivo in os.listdir("base_conhecimento"):
                if arquivo.endswith(".txt"):
                    try:
                        with open(f"base_conhecimento/{arquivo}", 'r', encoding='utf-8') as f:
                            textos.append(f"MANUAL: {f.read()[:3000]}")
                    except: pass
        
        # Junta tudo, mas limita o total para evitar o erro 429
        self.conhecimento_total = "\n\n".join(textos)[:150000]

@st.cache_resource
def iniciar_ia():
    obj = ImperiumCerebro()
    obj.carregar_arquivos()
    return obj

bot = iniciar_ia()

st.title("🤖 Imperium Bot (Gemini 2.5)")

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
        instrucao = f"""
        Você é o suporte técnico da Imperium TV.
        Seja curto, direto e educado.
        Use a base abaixo para responder. Se não encontrar a solução, peça para aguardar um humano.

        --- BASE DE CONHECIMENTO ---
        {bot.conhecimento_total}
        """

        try:
            # Modelo que apareceu no seu painel de uso
            model = genai.GenerativeModel('gemini-2.5-flash-lite')
            
            response = model.generate_content([instrucao, prompt])
            
            resposta_texto = response.text
            st.markdown(resposta_texto)
            st.session_state.messages.append({"role": "assistant", "content": resposta_texto})
            
        except Exception as e:
            if "429" in str(e):
                st.error("O Google está um pouco sobrecarregado. Por favor, aguarde 20 segundos e tente enviar novamente.")
            else:
                st.error(f"Ocorreu um erro: {e}")

st.sidebar.success("Sistema Conectado!")
st.sidebar.write("Dica: Evite mandar muitas mensagens por minuto para não travar a cota grátis.")
