import streamlit as st
import requests
from datetime import datetime

# Configuração da API do Grok (xAI)
API_URL = "https://api.x.ai/v1/chat/completions"  # Endpoint hipotético, verifique a documentação oficial
API_KEY = "xai-CniNRzYHesxo8WdzaVS2ADTHmymokXktCrOymlHEmESN0krZe8dMVucqTdjJKFHIWM7qDuQyA1lzFadY"  # Substitua pela sua chave API do Grok

# Função para obter resposta da API do Grok mantendo o contexto
def get_grok_response(messages):
    try:
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "grok",  # ou "grok-2" se aplicável, confirme na documentação
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        response = requests.post(API_URL, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Erro ao conectar com a API do Grok: {str(e)}"

# Inicialização do estado da sessão
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "Você é um assistente de suporte técnico útil. Responda às perguntas dos usuários com base no contexto fornecido e mantenha o tom profissional."}
    ]
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Configuração da interface
st.title("Chat de Suporte Técnico - Grok")
st.write("Faça sua pergunta abaixo e receba suporte baseado em nossa base de conhecimento.")

# Área de exibição do histórico do chat
chat_container = st.container()
with chat_container:
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(f"**{message['role'].capitalize()}**: {message['content']}")

# Formulário de entrada
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_area("Digite sua pergunta aqui:", height=100)
    submit_button = st.form_submit_button(label="Enviar")

# Processamento da entrada do usuário
if submit_button and user_input:
    # Adiciona a mensagem do usuário ao contexto
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    
    # Obtém a resposta da API do Grok
    with st.spinner("Gerando resposta..."):
        response = get_grok_response(st.session_state.messages)
    
    # Adiciona a resposta ao contexto e ao histórico
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.session_state.chat_history.append({"role": "assistant", "content": response})
    
    # Força a atualização da página
    st.rerun()

# Estilização adicional
st.markdown("""
    <style>
    .stTextArea textarea {
        border-radius: 10px;
        padding: 10px;
    }
    .stButton button {
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)