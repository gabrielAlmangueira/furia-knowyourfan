import streamlit as st
import requests
import json
import os
from datetime import datetime

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
st.title("Meu Perfil")
st.subheader("Informações Básicas")

# Obter perfil atual (se existir)
user_id = st.session_state.get("user_id", "user123")  # Fallback para teste
response = make_api_request(f"/api/profiles/{user_id}")

# Variáveis para armazenar os valores do formulário
profile_data = {}
if response and response.status_code == 200:
    profile_data = response.json()
    st.success("Perfil encontrado! Atualize suas informações se necessário.")
else:
    st.info("Complete seu perfil para continuar.")

# Formulário de perfil
with st.form("profile_form"):
    # Dados básicos
    full_name = st.text_input("Nome completo", value=profile_data.get("full_name", ""))
    cpf = st.text_input("CPF", value=profile_data.get("cpf", ""))
    
    # Dados de endereço
    st.subheader("Endereço")
    address = profile_data.get("address", {})
    
    col1, col2 = st.columns(2)
    with col1:
        city = st.text_input("Cidade", value=address.get("city", ""))
    with col2:
        state = st.text_input("Estado", value=address.get("state", ""))
    
    col1, col2 = st.columns(2)
    with col1:
        street = st.text_input("Rua/Avenida", value=address.get("street", ""))
    with col2:
        number = st.text_input("Número", value=address.get("number", ""))
    
    complement = st.text_input("Complemento", value=address.get("complement", ""))
    zipcode = st.text_input("CEP", value=address.get("zipcode", ""))
    
    # Dados de fã
    st.subheader("Informações como Fã da FURIA")
    fan_since = st.text_input("Desde quando você é fã da FURIA?", value=profile_data.get("furia_fan_since", ""))
    
    # Interesses
    interests_options = [
        "CS:GO", "Valorant", "League of Legends", "Rainbow Six", 
        "PUBG", "Fortnite", "Free Fire", "Fighting Games", "Outros"
    ]
    interests = st.multiselect(
        "Quais seus jogos/modalidades de interesse?",
        options=interests_options,
        default=profile_data.get("interests", [])
    )
    
    # Eventos
    st.subheader("Eventos que participou")
    events = st.text_area(
        "Liste os eventos da FURIA que você já participou (um por linha):",
        value="\n".join(profile_data.get("attended_events", []))
    )
    
    # Compras
    st.subheader("Compras realizadas")
    purchases = st.text_area(
        "Liste produtos da FURIA que você já adquiriu (um por linha):",
        value="\n".join(profile_data.get("purchases", []))
    )
    
    # Botão de salvar
    submitted = st.form_submit_button("Salvar Perfil")
    
    if submitted:
        if not full_name or not city or not state:
            st.error("Por favor, preencha todos os campos obrigatórios.")
        else:
            # Preparar dados para envio
            new_profile = {
                "full_name": full_name,
                "cpf": cpf,
                "address": {
                    "street": street,
                    "number": number,
                    "complement": complement,
                    "neighborhood": "",
                    "city": city,
                    "state": state,
                    "country": "Brasil",
                    "zipcode": zipcode
                },
                "interests": interests,
                "furia_fan_since": fan_since,
                "attended_events": [e.strip() for e in events.split("\n") if e.strip()],
                "purchases": [p.strip() for p in purchases.split("\n") if p.strip()]
            }
            
            # Verificar se já existe perfil
            if profile_data.get("id"):
                # Update
                response = make_api_request(
                    f"/api/profiles/{user_id}",
                    method="PUT",
                    data=new_profile
                )
            else:
                # Create
                response = make_api_request(
                    "/api/profiles",
                    method="POST",
                    data=new_profile
                )
            
            if response and response.status_code in [200, 201]:
                st.success("Perfil salvo com sucesso!")
            else:
                if response:
                    st.error(f"Erro ao salvar perfil: {response.json().get('detail', 'Erro desconhecido')}")
                else:
                    st.error("Erro de conexão com o servidor")

# Dicas úteis
with st.expander("Dicas úteis"):
    st.write("""
    - Preencha seu perfil completamente para uma melhor experiência
    - As informações de eventos e compras ajudarão a personalizar sua experiência
    - Você pode atualizar seu perfil a qualquer momento
    """)

# Voltar para o Dashboard
if st.button("Voltar para o Dashboard"):
    st.session_state["current_page"] = "dashboard"
    st.experimental_rerun()