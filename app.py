import streamlit as st
import requests
from bs4 import BeautifulSoup
import openai
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Suprimir os avisos de SSL
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Função para extrair conteúdo de uma página da web
def extract_content(url):
    response = requests.get(url, verify=False)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Captura uma maior variedade de tags (p, div, span) para coletar mais conteúdo
    content = ' '.join([p.get_text() for p in soup.find_all(['p', 'div', 'span'])])
    
    # Armazenar uma quantidade maior de conteúdo
    return content

# Função para gerar a resposta da API da OpenAI com base no conteúdo extraído
def generate_response_from_ai(api_key, site_content, question):
    try:
        openai.api_key = api_key
        
        # Criando um prompt que injeta o contexto do conteúdo extraído do site
        prompt = f"Here is the content from the site:\n{site_content}\nNow, based on this content, answer the following question: {question}"
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
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

if 'site_content' not in st.session_state:
    st.session_state['site_content'] = ""

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

# Subheader e divisória
st.subheader("Automação de Leitura de Sites")
st.divider()

# Entrada da URL e botão de processamento
url = st.text_input("Digite a URL do site:")

# Spinner para feedback do usuário
if st.button("Consultar site"):
    if url and st.session_state['api_connected']:
        with st.spinner('Processando o conteúdo da página...'):
            site_content = extract_content(url)
            st.session_state['site_content'] = site_content  # Armazena o conteúdo completo no session_state
            st.success("O conteúdo do site foi armazenado com sucesso. Agora você pode fazer perguntas.")
    else:
        st.error("Insira a URL e conecte a API antes de prosseguir.")

# Função para processar perguntas e respostas
def handle_question(question):
    if question and st.session_state['api_connected'] and st.session_state['site_content']:
        # Adiciona a pergunta ao histórico
        st.session_state['conversation_history'].append(f"User: {question}")
        
        # Gera a resposta usando o conteúdo armazenado
        response = generate_response_from_ai(api_key, st.session_state['site_content'], question)
        
        if response:
            # Adiciona a resposta ao histórico
            st.session_state['conversation_history'].append(f"AI: {response}")

# Campo de entrada no estilo de chat
user_input = st.chat_input("Digite sua pergunta...")
if user_input:
    handle_question(user_input)

# Exibindo o histórico de conversa
for message in st.session_state['conversation_history']:
    if message.startswith("User:"):
        st.chat_message("user").markdown(message.replace("User:", ""))
    else:
        st.chat_message("assistant").markdown(message.replace("AI:", ""))
