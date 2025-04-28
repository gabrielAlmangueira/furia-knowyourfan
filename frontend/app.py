import streamlit as st
import requests
import json
import os
from PIL import Image
import io

# Configurações da página
st.set_page_config(
    page_title="FURIA - Know Your Fan",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# URL da API
API_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Funções auxiliares
def make_api_request(endpoint, method="GET", data=None, files=None):
    """Função para fazer requisições à API"""
    url = f"{API_URL}{endpoint}"
    headers = {}
    
    # Adiciona token de autenticação se existir
    if "token" in st.session_state and st.session_state["token"]:
        headers["Authorization"] = f"Bearer {st.session_state['token']}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            if files:
                response = requests.post(url, headers=headers, data=data, files=files)
            else:
                response = requests.post(url, headers=headers, json=data)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            st.error("Método HTTP não suportado")
            return None
        
        return response
    except Exception as e:
        st.error(f"Erro na comunicação com a API: {str(e)}")
        return None

# Inicializar estado da sessão
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "token" not in st.session_state:
    st.session_state["token"] = None
if "user_id" not in st.session_state:
    st.session_state["user_id"] = None
if "username" not in st.session_state:
    st.session_state["username"] = None
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "home"

# Função de logout
def logout():
    st.session_state["logged_in"] = False
    st.session_state["token"] = None
    st.session_state["user_id"] = None
    st.session_state["username"] = None
    st.session_state["current_page"] = "home"
    st.experimental_rerun()

# Barra lateral
with st.sidebar:
    # Logo da FURIA
    st.image("https://seeklogo.com/images/F/furia-esports-logo-5A985353F3-seeklogo.com.png", width=150)
    st.title("Know Your Fan")
    
    # Menu para usuários não logados
    if not st.session_state["logged_in"]:
        st.subheader("Bem-vindo!")
        if st.button("Login"):
            st.session_state["current_page"] = "login"
            st.experimental_rerun()
        if st.button("Registrar"):
            st.session_state["current_page"] = "register"
            st.experimental_rerun()
    # Menu para usuários logados
    else:
        st.subheader(f"Olá, {st.session_state['username']}!")
        if st.button("Dashboard"):
            st.session_state["current_page"] = "dashboard"
            st.experimental_rerun()
        if st.button("Perfil"):
            st.session_state["current_page"] = "profile"
            st.experimental_rerun()
        if st.button("Documentos"):
            st.session_state["current_page"] = "documents"
            st.experimental_rerun()
        if st.button("Redes Sociais"):
            st.session_state["current_page"] = "social"
            st.experimental_rerun()
        if st.button("Perfis E-Sports"):
            st.session_state["current_page"] = "esports"
            st.experimental_rerun()
        if st.button("Logout"):
            logout()
    
    st.divider()
    st.caption("FURIA Esports © 2025")

# Renderização da página atual
if st.session_state["current_page"] == "home":
    st.title("🎮 FURIA - Know Your Fan")
    
    # Banner da FURIA
    st.image("https://static.wikia.nocookie.net/valorant_esports_gamepedia_en/images/0/0d/FURIA_Esportslogo_square.png", width=400)
    
    st.header("Conheça seu perfil de fã da FURIA Esports!")
    
    st.markdown("""
    ### Bem-vindo ao Know Your Fan!
    
    Esta plataforma foi projetada para conhecer melhor os fãs da FURIA e oferecer experiências e serviços exclusivos baseados no seu perfil.
    
    **O que você pode fazer aqui?**
    - Compartilhar suas informações básicas
    - Verificar sua identidade com segurança
    - Conectar suas redes sociais
    - Vincular seus perfis em plataformas de e-sports
    - Descobrir seu perfil de engajamento como fã
    
    **Faça seu cadastro ou login para começar!**
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Fazer Login", key="home_login"):
            st.session_state["current_page"] = "login"
            st.experimental_rerun()
    with col2:
        if st.button("Criar Conta", key="home_register"):
            st.session_state["current_page"] = "register"
            st.experimental_rerun()

elif st.session_state["current_page"] == "login":
    st.title("Login")
    
    with st.form("login_form"):
        username = st.text_input("Nome de usuário")
        password = st.text_input("Senha", type="password")
        submitted = st.form_submit_button("Entrar")
        
        if submitted:
            if not username or not password:
                st.error("Preencha todos os campos")
            else:
                # Fazer requisição para API de login
                response = make_api_request(
                    "/api/users/login",
                    method="POST",
                    data={"username": username, "password": password}
                )
                
                if response and response.status_code == 200:
                    data = response.json()
                    st.session_state["logged_in"] = True
                    st.session_state["token"] = data["access_token"]
                    st.session_state["user_id"] = data["user_id"]
                    st.session_state["username"] = data["username"]
                    st.session_state["current_page"] = "dashboard"
                    st.success("Login realizado com sucesso!")
                    st.experimental_rerun()
                else:
                    if response:
                        st.error(f"Falha no login: {response.json().get('detail', 'Erro desconhecido')}")
                    else:
                        st.error("Falha na conexão com o servidor")
    
    if st.button("Voltar"):
        st.session_state["current_page"] = "home"
        st.experimental_rerun()

elif st.session_state["current_page"] == "register":
    st.title("Criar Conta")
    
    with st.form("register_form"):
        username = st.text_input("Nome de usuário")
        email = st.text_input("E-mail")
        password = st.text_input("Senha", type="password")
        password_confirm = st.text_input("Confirme a senha", type="password")
        submitted = st.form_submit_button("Registrar")
        
        if submitted:
            if not username or not email or not password or not password_confirm:
                st.error("Preencha todos os campos")
            elif password != password_confirm:
                st.error("As senhas não correspondem")
            else:
                # Fazer requisição para API de registro
                response = make_api_request(
                    "/api/users/register",
                    method="POST",
                    data={"username": username, "email": email, "password": password}
                )
                
                if response and response.status_code == 200:
                    st.success("Conta criada com sucesso! Faça login para continuar.")
                    st.session_state["current_page"] = "login"
                    st.experimental_rerun()
                else:
                    if response:
                        st.error(f"Falha no registro: {response.json().get('detail', 'Erro desconhecido')}")
                    else:
                        st.error("Falha na conexão com o servidor")
    
    if st.button("Voltar"):
        st.session_state["current_page"] = "home"
        st.experimental_rerun()

elif st.session_state["current_page"] == "dashboard":
    if not st.session_state["logged_in"]:
        st.warning("Faça login para acessar esta página")
        if st.button("Ir para Login"):
            st.session_state["current_page"] = "login"
            st.experimental_rerun()
    else:
        st.title("Dashboard")
        st.subheader(f"Bem-vindo, {st.session_state['username']}!")
        
        # Layout do dashboard com métricas
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Perfil", "Incompleto", "-")
        with col2:
            st.metric("Documentos", "0/1", "-")
        with col3:
            st.metric("Redes Sociais", "0", "-")
        
        # Seção de conclusão de perfil
        st.subheader("Complete seu perfil")
        st.progress(0.0)
        
        st.write("Para completar seu perfil, siga os passos abaixo:")
        
        steps = {
            "Dados Básicos": {"status": "pendente", "page": "profile"},
            "Verificação de Identidade": {"status": "pendente", "page": "documents"},
            "Conexão de Redes Sociais": {"status": "pendente", "page": "social"},
            "Perfis de E-Sports": {"status": "pendente", "page": "esports"}
        }
        
        for step, info in steps.items():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"• {step}")
            with col2:
                if info["status"] == "pendente":
                    if st.button("Completar", key=f"complete_{info['page']}"):
                        st.session_state["current_page"] = info["page"]
                        st.experimental_rerun()
                else:
                    st.success("Concluído")
        
        # Placeholder para visualizações futuras
        st.subheader("Seu perfil como fã")
        st.info("Complete seu perfil para ver sua análise como fã da FURIA")

# Apenas um placeholder - as páginas reais seriam implementadas separadamente
else:
    st.title(f"Página: {st.session_state['current_page'].title()}")
    st.info("Esta página será implementada em breve!")
    
    if st.button("Voltar para o Dashboard"):
        st.session_state["current_page"] = "dashboard"
        st.experimental_rerun()