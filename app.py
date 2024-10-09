import streamlit as st
import requests
from bs4 import BeautifulSoup
import openai

# Função para extrair conteúdo de um site
def extract_content(url):
    response = requests.get(url, verify=False)  # Ignorando a verificação SSL para facilitar o teste
    soup = BeautifulSoup(response.content, 'html.parser')
    return ' '.join([p.get_text() for p in soup.find_all('p')])

# Função para gerar resposta da OpenAI com contexto
def generate_response_from_ai(api_key, conversation_history, question):
    openai.api_key = api_key
    conversation = "\n".join(conversation_history)  # Concatenando o histórico da conversa
    prompt = f"Here is the conversation so far:\n{conversation}\nAnswer the following question: {question}"
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        max_tokens=150
    )
    return response['choices'][0]['text']

# Inicializando o histórico de conversa na sessão
if 'conversation_history' not in st.session_state:
    st.session_state['conversation_history'] = []

if 'api_connected' not in st.session_state:
    st.session_state['api_connected'] = False

# Interface Streamlit - Sidebar para API
st.sidebar.title("Configurações")
api_key = st.sidebar.text_input("Insira sua chave da API da OpenAI", type="password")
if st.sidebar.button("Conectar API"):
    if api_key:
        st.session_state['api_connected'] = True
        st.sidebar.success("API conectada com sucesso!")
    else:
        st.sidebar.error("Por favor, insira uma chave de API válida.")

# Interface Streamlit - Chat
st.title("Automação de Leitura de Sites")
url = st.text_input("Digite a URL do site:")

# Botão para consultar o site e resetar a memória
if st.button("Consultar site"):
    if url and st.session_state['api_connected']:
        site_content = extract_content(url)
        st.session_state['conversation_history'] = []  # Resetando a memória do chatbot
        st.session_state['conversation_history'].append(f"Site content: {site_content[:500]}")  # Armazenando parte do conteúdo
        st.success("O conteúdo do site foi armazenado e a memória foi resetada.")
    else:
        st.error("Insira a URL e conecte a API antes de prosseguir.")

# Campo para fazer perguntas estilo chat
def handle_question():
    question = st.session_state['user_input']
    if question and st.session_state['api_connected']:
        # Adiciona a pergunta ao histórico
        st.session_state['conversation_history'].append(f"User: {question}")
        response = generate_response_from_ai(api_key, st.session_state['conversation_history'], question)
        # Adiciona a resposta ao histórico
        st.session_state['conversation_history'].append(f"AI: {response}")
        st.session_state['user_input'] = ""  # Limpa o campo de entrada após o envio

# Caixa de texto estilo chat
st.text_input("Digite sua pergunta:", key='user_input', on_change=handle_question)

# Exibindo o histórico de conversa
for message in st.session_state['conversation_history']:
    if message.startswith("User:"):
        st.text_area("Você:", message.replace("User:", ""), key=message, height=50)
    else:
        st.text_area("Assistente:", message.replace("AI:", ""), key=message, height=50)
