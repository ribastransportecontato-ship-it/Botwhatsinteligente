import streamlit as st
import os
import json
import google.generativeai as genai

# Configuração da sua Chave de API
GOOGLE_API_KEY = "AIzaSyCkCY0C6iehoiybkzrxAzvyh5aV9SwUKyE"

# Configuração crucial para evitar o erro 404 (força a comunicação estável)
genai.configure(api_key=GOOGLE_API_KEY, transport='rest')

st.set_page_config(page_title="Imperium IA - Atendimento", layout="wide")

class ImperiumHumano:
    def __init__(self):
        self.conhecimento = ""

    def carregar_aprendizado(self):
        """Lê todos os arquivos do GitHub para criar o cérebro da IA"""
        dados_totais = []
        
        # 1. Carrega os Fluxos do Botbot (JSON)
        if os.path.exists("fluxos_json"):
            for arq in os.listdir("fluxos_json"):
                if arq.endswith(".json"):
                    try:
                        with open(f"fluxos_json/{arq}", 'r', encoding='utf-8') as f:
                            conteudo = json.load(f)
                            # Transforma o JSON em texto simples para a IA entender
                            dados_totais.append(f"Fluxo: {arq} - Conteúdo: {json.dumps(conteudo, ensure_ascii=False)}")
                    except:
                        pass
        
        # 2. Carrega os Manuais (TXT)
        if os.path.exists("base_conhecimento"):
            for arq in os.listdir("base_conhecimento"):
                if arq.endswith(".txt"):
                    try:
                        with open(f"base_conhecimento/{arq}", 'r', encoding='utf-8') as f:
                            dados_totais.append(f"Manual: {f.read()}")
                    except:
                        pass
        
        self.conhecimento = "\n---\n".join(dados_totais)

# Inicializa e carrega o conhecimento
@st.cache_resource
def iniciar_bot():
    bot = ImperiumHumano()
    bot.carregar_aprendizado()
    return bot

bot = iniciar_bot()

# Interface do Chat
st.title("🤖 Imperium Bot - IA Humana")
st.caption("Atendimento Inteligente baseado nos seus tutoriais")

# Histórico da conversa para parecer um chat real
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Campo de entrada do cliente
if prompt := st.chat_input("Como posso te ajudar hoje?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Prepara a instrução para a IA ser humana
        instrucao = f"""
        Você é o 'Imperium Bot', o atendente humano da Imperium TV. 
        Sua missão é ajudar os clientes de forma gentil, educada e clara.

        INSTRUÇÕES DE COMPORTAMENTO:
        - Não responda de forma robótica.
        - Use as informações abaixo para dar soluções técnicas.
        - Se o cliente perguntar algo que não está nos manuais, diga que vai verificar com o suporte técnico humano.

        BASE DE CONHECIMENTO (TUTORIAIS E FLUXOS):
        {bot.conhecimento}

        PERGUNTA DO CLIENTE:
        {prompt}
        """

        try:
            # Tenta usar o modelo Flash (mais rápido)
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(instrucao)
            
            texto_resposta = response.text
            st.markdown(texto_resposta)
            st.session_state.messages.append({"role": "assistant", "content": texto_resposta})
            
        except Exception as e:
            # Caso o modelo Flash falhe por versão, tenta o modelo estável padrão
            try:
                model_alt = genai.GenerativeModel('gemini-pro')
                response = model_alt.generate_content(instrucao)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e2:
                st.error("Desculpe, tive um problema técnico na minha conexão de IA. Pode tentar novamente?")
                st.write(f"Detalhe do erro: {e2}")

# Rodapé com status
st.sidebar.markdown("---")
st.sidebar.write(f"🧠 Conhecimento carregado.")
