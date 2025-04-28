import streamlit as st
import requests
import os
import pandas as pd
from PIL import Image
import io

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

# Verificar se o usuário está logado
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.warning("Faça login para acessar esta página")
    st.stop()

# Título da página
st.title("Perfis de E-Sports")
st.subheader("Vincule seus perfis de jogos e plataformas")

# Obter perfis existentes do usuário
user_id = st.session_state.get("user_id", "user123")  # Fallback para teste
response = make_api_request(f"/api/esports/user/{user_id}")

# Mostrar perfis vinculados
if response and response.status_code == 200:
    profiles = response.json()
    if profiles:
        st.write("### Perfis vinculados")
        
        # Criar tabela com os perfis
        for profile in profiles:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col1:
                platform = profile["platform"].upper()
                st.image(f"https://www.google.com/s2/favicons?domain={platform}.com&sz=64", width=50)
            with col2:
                st.write(f"**{platform}**")
                st.write(f"Usuário: {profile['username']}")
                st.write(f"[Ver perfil]({profile['profile_url']})")
            with col3:
                if profile.get("verified"):
                    st.success("Verificado ✓")
                else:
                    st.warning("Não verificado")
                    
                    # Botão para verificar perfil
                    if st.button(f"Verificar {platform}", key=f"verify_{profile['id']}"):
                        st.session_state["profile_to_verify"] = profile["id"]
            
            st.divider()
    else:
        st.info("Você ainda não vinculou nenhum perfil de e-sports")

# Se um perfil foi selecionado para verificação
if "profile_to_verify" in st.session_state:
    profile_id = st.session_state["profile_to_verify"]
    st.subheader("Verificação de perfil")
    st.info("""
    Para verificar seu perfil, faça upload de uma captura de tela mostrando você logado na plataforma.
    A imagem deve exibir claramente seu nome de usuário.
    """)
    
    uploaded_file = st.file_uploader("Upload da captura de tela", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        # Mostrar imagem
        image = Image.open(uploaded_file)
        st.image(image, caption="Captura de tela enviada", width=400)
        
        # Botão de envio
        if st.button("Enviar para verificação"):
            # Preparar arquivo para envio
            file_bytes = uploaded_file.getvalue()
            
            # Enviar para API
            files = {"screenshot": (uploaded_file.name, file_bytes, f"image/{uploaded_file.type.split('/')[1]}")}
            response = make_api_request(
                f"/api/esports/verify/{profile_id}",
                method="POST",
                files=files
            )
            
            if response and response.status_code in [200, 201]:
                st.success("Screenshot enviado com sucesso! Seu perfil será verificado em breve.")
                # Limpar o estado de verificação
                del st.session_state["profile_to_verify"]
                st.experimental_rerun()
            else:
                if response:
                    st.error(f"Erro ao verificar perfil: {response.json().get('detail', 'Erro desconhecido')}")
                else:
                    st.error("Erro de conexão com o servidor")
    
    # Cancelar verificação
    if st.button("Cancelar"):
        del st.session_state["profile_to_verify"]
        st.experimental_rerun()

# Formulário para adicionar novo perfil
st.write("### Vincular novo perfil")

platforms = {
    "steam": "Steam",
    "faceit": "FACEIT",
    "battlefy": "Battlefy",
    "riot": "Riot Games",
    "epic": "Epic Games"
}

with st.form("add_esports_form"):
    platform = st.selectbox(
        "Plataforma",
        options=list(platforms.keys()),
        format_func=lambda x: platforms[x]
    )
    
    username = st.text_input("Nome de usuário")
    profile_url = st.text_input("URL do perfil")
    
    submit_profile = st.form_submit_button("Vincular")
    
    if submit_profile:
        if not username or not profile_url:
            st.error("Preencha todos os campos")
        else:
            # Preparar dados para envio
            profile_data = {
                "platform": platform,
                "username": username,
                "profile_url": profile_url
            }
            
            # Enviar dados
            response = make_api_request(
                "/api/esports/",
                method="POST",
                data=profile_data
            )
            
            if response and response.status_code in [200, 201]:
                st.success(f"Perfil {platforms[platform]} vinculado com sucesso!")
                st.experimental_rerun()
            else:
                if response:
                    st.error(f"Erro ao vincular perfil: {response.json().get('detail', 'Erro desconhecido')}")
                else:
                    st.error("Erro de conexão com o servidor")

# Informações sobre a importância dos perfis
with st.expander("Por que vincular perfis de e-sports?"):
    st.write("""
    ### Benefícios de vincular seus perfis de jogos
    
    Ao vincular seus perfis de e-sports, você:
    
    - **Valida** sua identidade como jogador
    - **Demonstra** seu interesse em jogos específicos
    - **Recebe** recomendações personalizadas de eventos e conteúdo
    - **Conecta-se** com outros fãs da FURIA com interesses similares
    - **Participa** de promoções exclusivas para jogadores
    
    Os perfis verificados têm prioridade em sorteios e eventos exclusivos!
    """)

# Voltar para o Dashboard
if st.button("Voltar para o Dashboard"):
    st.session_state["current_page"] = "dashboard"
    st.experimental_rerun()