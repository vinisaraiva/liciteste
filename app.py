import streamlit as st
import requests
from bs4 import BeautifulSoup
import openai

# Função para extrair conteúdo de um site
def extract_content(url):
    response = requests.get(url)
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

# Interface Streamlit
st.sidebar.title("Configurações")
api_key = st.sidebar.text_input("Insira sua chave da API da OpenAI", type="password")

st.title("Automação de Leitura de Sites")
url = st.text_input("Digite a URL do site:")

# Botão para consultar o site e resetar a memória
if st.button("Consultar site"):
    if url and api_key:
        site_content = extract_content(url)
        st.session_state['conversation_history'] = []  # Resetando a memória do chatbot
        st.session_state['conversation_history'].append(f"Site content: {site_content[:500]}")  # Armazenando parte do conteúdo
        st.success("O conteúdo do site foi armazenado e a memória foi resetada.")
    else:
        st.error("Insira a URL e a chave da API.")

# Campo para fazer perguntas
question = st.text_input("Faça uma pergunta:")
if st.button("Obter resposta"):
    if api_key and 'site_content' in locals():
        # Adiciona a pergunta ao histórico
        st.session_state['conversation_history'].append(f"User: {question}")
        response = generate_response_from_ai(api_key, st.session_state['conversation_history'], question)
        # Adiciona a resposta ao histórico
        st.session_state['conversation_history'].append(f"AI: {response}")
        st.write(response)
    else:
        st.error("Insira a chave da API e consulte o site antes de fazer uma pergunta.")
