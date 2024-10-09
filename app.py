import streamlit as st
import requests
from bs4 import BeautifulSoup
import openai

# Função para extrair conteúdo de um site
def extract_content(url):
    response = requests.get(url, verify=False)  # Ignorando a verificação SSL para facilitar o teste
    soup = BeautifulSoup(response.content, 'html.parser')
    return ' '.join([p.get_text() for p in soup.find_all('p')])

# Função para gerar resposta da OpenAI com contexto usando o modelo gpt-3.5-turbo
def generate_response_from_ai(api_key, conversation_history, question):
    try:
        openai.api_key = api_key
        conversation = [{"role": "system", "content": "You are a helpful assistant."}]
        conversation += [{"role": "user", "content": message} for message in conversation_history]
        conversation.append({"role": "user", "content": question})

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=conversation
        )
        return response['choices'][0]['message']['content']
    except openai.error.AuthenticationError:
        st.error("Falha na autenticação: a chave da API da OpenAI está incorreta.")
        return None
    except openai.error.InvalidRequestError as e:
        st.error(f"Erro na solicitação: {e}")
        return None

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

# Inserir imagem de cabeçalho
st.image("header.png", use_column_width=True)
st.markdown("<style>div.stImage > img { padding-top: 0px; }</style>", unsafe_allow_html=True)

# Interface Streamlit - Subheader com divisória
st.subheader("Automação de Leitura de Sites", divider=True)

# Botão para consultar o site e resetar a memória
url = st.text_input("Digite a URL do site:")
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
        if response:
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
