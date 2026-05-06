import streamlit as st
import os
import json
import google.generativeai as genai

# Puxa a chave do Render
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

st.set_page_config(page_title="Imperium Bot - Suporte Técnico", layout="wide")

class ImperiumCerebro:
    def __init__(self):
        self.conhecimento_total = ""

    def carregar_arquivos(self):
        textos = []
        # Carregar arquivos JSON
        if os.path.exists("fluxos_json"):
            for arquivo in os.listdir("fluxos_json"):
                if arquivo.endswith(".json"):
                    try:
                        with open(f"fluxos_json/{arquivo}", 'r', encoding='utf-8') as f:
                            dados = json.load(f)
                            # Enviamos o conteúdo mais completo agora
                            textos.append(f"ARQUIVO: {arquivo}\nCONTEUDO: {json.dumps(dados, ensure_ascii=False)}")
                    except: pass
        
        # Carregar TXT
        if os.path.exists("base_conhecimento"):
            for arquivo in os.listdir("base_conhecimento"):
                if arquivo.endswith(".txt"):
                    try:
                        with open(f"base_conhecimento/{arquivo}", 'r', encoding='utf-8') as f:
                            textos.append(f"MANUAL: {f.read()}")
                    except: pass
        
        # O Gemini 2.5 Flash Lite aguenta muito, vamos mandar até 200 mil tokens
        self.conhecimento_total = "\n\n---\n\n".join(textos)[:200000]

@st.cache_resource
def iniciar_ia():
    obj = ImperiumCerebro()
    obj.carregar_arquivos()
    return obj

bot = iniciar_ia()

st.title("🤖 Suporte Imperium TV")

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
        # REGRAS MAIS RÍGIDAS PARA EVITAR RESPOSTAS ERRADAS
        instrucao = f"""
        Você é o Especialista em Suporte da Imperium TV.
        
        SUA REGRA DE OURO:
        1. Analise a pergunta do cliente.
        2. Busque na base abaixo a solução EXATA para o problema citado.
        3. Se o cliente reclama de TRAVAMENTO, foque em: limpeza de cache, troca de player ou verificação de internet.
        4. NÃO sugira "Troca de Região" da TV a menos que o cliente diga que o app NÃO APARECE na loja.
        5. Se não encontrar a resposta exata, diga: "Vou verificar seu caso detalhadamente com a equipe técnica, um momento."

        BASE DE DADOS:
        {bot.conhecimento_total}
        """

        try:
            model = genai.GenerativeModel('gemini-2.5-flash-lite')
            # Usamos uma temperatura menor (0.3) para ele ser mais "pé no chão" e menos criativo
            response = model.generate_content(
                [instrucao, prompt],
                generation_config=genai.types.GenerationConfig(temperature=0.3)
            )
            
            resposta_texto = response.text
            st.markdown(resposta_texto)
            st.session_state.messages.append({"role": "assistant", "content": resposta_texto})
            
        except Exception as e:
            if "429" in str(e):
                st.error("Aguarde 20 segundos para a próxima pergunta.")
            else:
                st.error(f"Erro: {e}")
