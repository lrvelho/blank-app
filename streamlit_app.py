import streamlit as st
import requests
import pandas as pd
import json

# Configuração da API do Grok (xAI)
API_URL = "https://api.x.ai/v1/chat/completions"
API_KEY = "xai-CniNRzYHesxo8WdzaVS2ADTHmymokXktCrOymlHEmESN0krZe8dMVucqTdjJKFHIWM7qDuQyA1lzFadY"




# Função para carregar o contexto a partir de um arquivo JSON
def load_context_file(file_path="Context/context.json"):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        # Certifica-se de que o JSON contém a estrutura esperada
        if not isinstance(data, list):
            raise ValueError("O arquivo JSON deve ser uma lista de objetos com as chaves 'pais' e 'quantidade'.")

        for item in data:
            if "pais" not in item or "quantidade" not in item:
                raise ValueError("Cada entrada do JSON deve conter as chaves 'pais' e 'quantidade'.")

        # Converte para DataFrame para formatação similar à do Excel
        df = pd.DataFrame(data)
        df.columns = [col.strip().lower() for col in df.columns]  # Normaliza os nomes das colunas

        return f"Contexto do arquivo JSON ({file_path}):\n{df.to_string(index=False)}"

    except Exception as e:
        return f"Erro ao carregar o arquivo de contexto: {str(e)}"
    

# Função para obter resposta da API do Grok
def get_grok_response(messages):
    try:
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "grok-2-latest",
            "messages": messages,
            "stream": False,
            "temperature": 0,  # Temperatura baixa para respostas mais consistentes
            "max_tokens": 1000
        }
        response = requests.post(API_URL, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Erro ao conectar com a API do Grok: {str(e)}"

# Carrega o contexto fixo ao iniciar e inicializa o estado da sessão
if "messages" not in st.session_state:
    context_content = load_context_file("Context/context.json")
    st.session_state.messages = [
        {
            "role": "system",
            "content": (
                "Você é um assistente de suporte técnico que responde exclusivamente com base no contexto fornecido pelo arquivo context.json. "
                "Este arquivo contém a quantidade de prêmios Nobel por país, com as colunas 'pais' e 'quantidade', onde 'pais' é o nome do país e 'quantidade' é o número total de prêmios Nobel recebidos por aquele país. "
                "Responda perguntas como 'Quantos Nobel tem [país]?' ou 'Qual a quantidade de prêmios Nobel de [país]?' usando apenas os dados deste arquivo. "
                "Não use conhecimento externo ou outros dados além do conteúdo deste arquivo. "
                "Se a pergunta não puder ser respondida com base nesse contexto (por exemplo, se o país não estiver listado ou se a pergunta não se relacionar com prêmios Nobel), "
                "responda exatamente: 'Não tenho como informar a resposta com base no contexto fornecido.' "
                "Formate suas respostas em Markdown para melhor legibilidade, usando cabeçalhos (#), listas (-), negrito (**), etc., "
                "quando apropriado.\n\n"
                f"{context_content}"
            )
        }
    ]
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Configuração da interface
st.image("Images/LogoLuminaGrande.png", width=200)
st.title("Chat de Suporte Técnico - Lumina")
st.write("Faça sua pergunta. As respostas serão baseadas exclusivamente no contexto da planilha fixa sobre prêmios Nobel por país.")

# Área de exibição do histórico do chat
chat_container = st.container()
with chat_container:
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            if message["role"] == "assistant":
                st.markdown(message["content"])
            else:
                st.markdown(f"**{message['role'].capitalize()}**: {message['content']}")

# Formulário de entrada (sem upload de arquivo)
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_area("Digite sua pergunta aqui:", height=100)
    submit_button = st.form_submit_button(label="Enviar")

# Processamento da entrada do usuário
if submit_button and user_input:
    # Adiciona a pergunta ao histórico, mas só envia a pergunta ao Grok com o contexto fixo
    user_message = user_input.strip()
    st.session_state.chat_history.append({"role": "user", "content": user_message})
    
    # Envia apenas a pergunta e o contexto fixo inicial ao Grok
    messages_to_send = st.session_state.messages + [{"role": "user", "content": user_message}]
    
    with st.spinner("Gerando resposta..."):
        response = get_grok_response(messages_to_send)
    
    st.session_state.messages.append({"role": "user", "content": user_message})
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.session_state.chat_history.append({"role": "assistant", "content": response})
    
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