import streamlit as st
import os
import json

# Configuração da página do seu sistema
st.set_page_config(page_title="Imperium Bot - Central", layout="wide")

class EngineBot:
    def __init__(self):
        self.caminho_fluxos = "fluxos_json"
        self.caminho_conhecimento = "base_conhecimento"
        self.memoria = {}
        self.manuais = ""

    def carregar_dados(self):
        # 1. Tenta ler a pasta de JSONs (Fluxos do Chatbot)
        if os.path.exists(self.caminho_fluxos):
            for item in os.listdir(self.caminho_fluxos):
                if item.endswith(".json"):
                    caminho = os.path.join(self.caminho_fluxos, item)
                    with open(caminho, 'r', encoding='utf-8') as f:
                        try:
                            data = json.load(f)
                            # Organiza pela palavra-chave para o bot saber responder
                            key = data.get("keyword", "sem_nome").lower()
                            self.memoria[key] = data
                        except:
                            pass

        # 2. Tenta ler a pasta de Manuais (Aprendizado da IA)
        if os.path.exists(self.caminho_conhecimento):
            textos = []
            for item in os.listdir(self.caminho_conhecimento):
                if item.endswith(".txt"):
                    caminho = os.path.join(self.caminho_conhecimento, item)
                    with open(caminho, 'r', encoding='utf-8') as f:
                        textos.append(f.read())
            self.manuais = "\n\n".join(textos)

# Inicializa o processador de dados
bot = EngineBot()
bot.carregar_dados()

st.title("🤖 Imperium Bot - Sistema de Gestão")

# Barra lateral com resumo do que o bot aprendeu
st.sidebar.header("Status de Aprendizado")
st.sidebar.write(f"📁 JSONs lidos: **{len(bot.memoria)}**")
st.sidebar.write(f"📄 Manuais ativos: **{len(bot.manuais.splitlines()) if bot.manuais else 0} linhas**")

st.info("Este bot lê automaticamente os arquivos que você coloca no GitHub.")

# Campo de teste para simular o cliente
pergunta = st.text_input("Simule uma mensagem do cliente (ex: 'localizando mac ib'):")

if pergunta:
    resultado = bot.memoria.get(pergunta.lower())
    if resultado:
        st.subheader("✅ Resposta configurada encontrada:")
        if "replies" in resultado:
            for r in resultado["replies"]:
                st.info(r.get("reply"))
    else:
        st.warning("❌ Nenhuma resposta JSON encontrada para esta palavra-chave.")

st.divider()

# Mostra o que a IA aprendeu com os TXTs
with st.expander("Visualizar Base de Conhecimento (Textos de Apoio)"):
    if bot.manuais:
        st.text(bot.manuais)
    else:
        st.write("A pasta 'base_conhecimento' ainda está vazia ou sem arquivos .txt")
