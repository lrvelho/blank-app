import streamlit as st
import requests
import base64
from datetime import datetime
import PyPDF2  # Para ler PDFs
import pandas as pd  # Para ler Excel
from io import BytesIO

# Configuração da API do Grok (xAI)
API_URL = "https://api.x.ai/v1/chat/completions"
API_KEY = "xai-CniNRzYHesxo8WdzaVS2ADTHmymokXktCrOymlHEmESN0krZe8dMVucqTdjJKFHIWM7qDuQyA1lzFadY"  # Sua chave API

# Função para extrair texto de arquivos
def extract_file_content(uploaded_file):
    if uploaded_file is None:
        return None
    
    file_type = uploaded_file.type
    file_name = uploaded_file.name
    
    if file_type == "text/plain":
        # Arquivos de texto
        return uploaded_file.read().decode("utf-8")
    
    elif file_type == "application/pdf":
        # Arquivos PDF
        pdf_reader = PyPDF2.PdfReader(BytesIO(uploaded_file.read()))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
        return text
    
    elif file_type in ["image/png", "image/jpeg"]:
        # Imagens (codifica em base64)
        image_data = uploaded_file.read()
        base64_image = base64.b64encode(image_data).decode("utf-8")
        return f"Imagem ({file_name}) codificada em base64: {base64_image}"
    
    elif file_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        # Arquivos Excel (.xlsx)
        df = pd.read_excel(BytesIO(uploaded_file.read()))
        # Converte o DataFrame para string em formato de tabela
        return f"Tabela do arquivo ({file_name}):\n{df.to_string(index=False)}"
    
    else:
        return f"Tipo de arquivo não suportado: {file_type}"

# Função para obter resposta da API do Grok mantendo o contexto
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
            "temperature": 0,
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
        {"role": "system", "content": "Você é um assistente de suporte técnico útil. Responda às perguntas dos usuários com base no contexto fornecido, incluindo o conteúdo de arquivos anexados (texto, PDFs, imagens ou planilhas Excel). Formate suas respostas em Markdown para melhor legibilidade, usando cabeçalhos (#), listas (-), negrito (**), etc., quando apropriado."}
    ]
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Configuração da interface
st.image( "Images/LogoLuminaGrande.png", width=100)  # Substitua pelo caminho do seu logo
st.title("Chat de Suporte Técnico - Lumina")
st.write("Faça sua pergunta e anexe arquivos (texto, PDF, imagens ou Excel) para análise.")


# Configuração da interface
col1, col2 = st.columns([1, 3])  # Ajuste as proporções conforme necessário
with col1:
    st.image( "Images/LogoLuminaGrande.png", width=100)  # Substitua pelo caminho do seu logo
with col2:
    st.title("Chat de Suporte Técnico - Lumina")




# Área de exibição do histórico do chat
chat_container = st.container()
with chat_container:
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            if message["role"] == "assistant":
                st.markdown(message["content"])
            else:
                st.markdown(f"**{message['role'].capitalize()}**: {message['content']}")

# Formulário de entrada com upload de arquivo
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_area("Digite sua pergunta aqui:", height=100)
    uploaded_file = st.file_uploader("Anexe um arquivo (opcional):", type=["txt", "pdf", "png", "jpg", "jpeg", "xlsx"])
    submit_button = st.form_submit_button(label="Enviar")

# Processamento da entrada do usuário
if submit_button and (user_input or uploaded_file):
    # Constrói a mensagem do usuário
    user_message = ""
    if user_input:
        user_message += user_input
    
    # Extrai e adiciona o conteúdo do arquivo, se houver.
    if uploaded_file:
        file_content = extract_file_content(uploaded_file)
        if file_content:
            user_message += f"\n\n**Conteúdo do arquivo ({uploaded_file.name})**:\n{file_content}"
    
    if user_message:
        st.session_state.messages.append({"role": "user", "content": user_message})
        st.session_state.chat_history.append({"role": "user", "content": user_message})
        
        with st.spinner("Gerando resposta..."):
            response = get_grok_response(st.session_state.messages)
        
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