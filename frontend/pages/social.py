import streamlit as st
import requests
import os
import pandas as pd
import plotly.express as px

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
st.title("Redes Sociais")
st.subheader("Conecte suas redes sociais")

# Obter redes sociais existentes do usuário
user_id = st.session_state.get("user_id", "user123")  # Fallback para teste
response = make_api_request(f"/api/social/user/{user_id}")

# Mostrar redes sociais conectadas
if response and response.status_code == 200:
    accounts = response.json()
    if accounts:
        st.write("### Redes sociais conectadas")
        
        # Criar tabela com as redes sociais
        accounts_data = []
        for account in accounts:
            accounts_data.append({
                "ID": account["id"],
                "Plataforma": account["platform"].capitalize(),
                "Username": account["username"],
                "Relevância": account.get("relevance_score", 0) * 100
            })
        
        accounts_df = pd.DataFrame(accounts_data)
        
        # Mostrar tabela
        st.dataframe(accounts_df[["Plataforma", "Username", "Relevância"]], width=800)
        
        # Criar gráfico de relevância
        if not accounts_df.empty:
            fig = px.bar(
                accounts_df, 
                x="Plataforma", 
                y="Relevância",
                color="Plataforma",
                title="Relevância das suas redes sociais para FURIA",
                labels={"Relevância": "Pontuação de Relevância (%)"}
            )
            st.plotly_chart(fig)
            
            # Adicionar botão para analisar manualmente
            st.write("### Analisar relevância")
            st.info("Clique no botão abaixo para analisar a relevância das suas redes sociais")
            
            if st.button("Analisar redes sociais"):
                with st.spinner("Analisando suas redes sociais..."):
                    # Na versão completa, chamar a API para cada conta
                    # Aqui, apenas simulamos a análise
                    st.success("Análise concluída com sucesso!")
                    st.info("Atualize a página para ver os resultados atualizados")
            
        # Adicionar botão para remover conta
        with st.expander("Gerenciar contas"):
            account_to_delete = st.selectbox(
                "Selecione uma conta para desconectar",
                options=accounts_df["ID"].tolist(),
                format_func=lambda x: f"{accounts_df.loc[accounts_df['ID'] == x, 'Plataforma'].iloc[0]} - {accounts_df.loc[accounts_df['ID'] == x, 'Username'].iloc[0]}"
            )
            
            if st.button("Desconectar conta"):
                response = make_api_request(f"/api/social/{account_to_delete}", method="DELETE")
                
                if response and response.status_code in [200, 204]:
                    st.success("Conta desconectada com sucesso!")
                    st.experimental_rerun()
                else:
                    st.error("Erro ao desconectar conta")
    else:
        st.info("Você ainda não conectou nenhuma rede social")

# Formulário para adicionar nova rede social
st.write("### Conectar nova rede social")

# Em um produto completo, usaríamos OAuth para cada plataforma
# Para o MVP, usamos um formulário manual simples

platforms = {
    "twitter": "Twitter/X",
    "instagram": "Instagram",
    "facebook": "Facebook",
    "discord": "Discord",
    "twitch": "Twitch"
}

with st.form("add_social_form"):
    platform = st.selectbox(
        "Plataforma",
        options=list(platforms.keys()),
        format_func=lambda x: platforms[x]
    )
    
    username = st.text_input("Nome de usuário")
    profile_url = st.text_input("URL do perfil")
    
    submit_social = st.form_submit_button("Conectar")
    
    if submit_social:
        if not username or not profile_url:
            st.error("Preencha todos os campos")
        else:
            # Preparar dados para envio
            social_data = {
                "platform": platform,
                "username": username,
                "profile_url": profile_url
            }
            
            # Enviar dados
            response = make_api_request(
                "/api/social/",
                method="POST",
                data=social_data
            )
            
            if response and response.status_code in [200, 201]:
                st.success(f"Conta {platforms[platform]} conectada com sucesso!")
                st.experimental_rerun()
            else:
                if response:
                    st.error(f"Erro ao conectar conta: {response.json().get('detail', 'Erro desconhecido')}")
                else:
                    st.error("Erro de conexão com o servidor")

# Informações sobre a relevância
with st.expander("Sobre a análise de relevância"):
    st.write("""
    ### Como calculamos a relevância
    
    A análise de relevância avalia seu engajamento com conteúdo da FURIA Esports nas redes sociais:
    
    - **Publicações**: Menções à FURIA, seus times e jogadores
    - **Curtidas**: Interações com publicações oficiais
    - **Compartilhamentos**: Divulgação de conteúdo relacionado
    - **Hashtags**: Uso de hashtags oficiais ou relacionadas
    - **Seguindo**: Seguir perfis oficiais e relacionados
    
    Quanto mais alto seu score, maior seu engajamento como fã!
    """)

# Voltar para o Dashboard
if st.button("Voltar para o Dashboard"):
    st.session_state["current_page"] = "dashboard"
    st.experimental_rerun()