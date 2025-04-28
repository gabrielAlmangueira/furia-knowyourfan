import streamlit as st
import requests
import os
from PIL import Image
import io
from streamlit_webrtc import webrtc_streamer
import av
import cv2
import numpy as np

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

# Função para capturar frame da webcam
class VideoProcessor:
    def __init__(self):
        self.frame = None
        self.capture_requested = False
        self.capture_done = False

    def request_capture(self):
        self.capture_requested = True
        self.capture_done = False

    def process(self, frame):
        img = frame.to_ndarray(format="bgr24")
        
        # Se solicitado, captura frame atual
        if self.capture_requested:
            self.frame = img.copy()
            self.capture_requested = False
            self.capture_done = True
            
        # Desenha texto indicando como capturar
        cv2.putText(
            img, 
            "Clique em 'Capturar Selfie' quando estiver pronto", 
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX, 
            0.7, 
            (0, 255, 0),
            2
        )
            
        return av.VideoFrame.from_ndarray(img, format="bgr24")

# Verificar se o usuário está logado
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.warning("Faça login para acessar esta página")
    st.stop()

# Título da página
st.title("Verificação de Documentos")

# Inicializar estados da sessão para este módulo
if 'document_processor' not in st.session_state:
    st.session_state.document_processor = VideoProcessor()
if 'selfie_captured' not in st.session_state:
    st.session_state.selfie_captured = False
if 'document_uploaded' not in st.session_state:
    st.session_state.document_uploaded = False

# Obter documentos existentes do usuário
user_id = st.session_state.get("user_id", "user123")  # Fallback para teste
response = make_api_request(f"/api/documents/status/{user_id}")

# Verificar se o usuário já tem documentos verificados
has_verified_docs = False
if response and response.status_code == 200:
    documents = response.json()
    if documents:
        st.subheader("Seus documentos")
        for doc in documents:
            status = doc.get("verification_status", "pendente")
            status_color = "green" if status == "verified" else "orange"
            st.markdown(f"**Documento:** {doc.get('document_type')} - **Status:** :{status_color}[{status}]")
            has_verified_docs = has_verified_docs or status == "verified"
        
        if has_verified_docs:
            st.success("Você já tem documentos verificados! Não é necessário enviar novos documentos.")

# Upload de novos documentos
st.subheader("Upload de documento de identidade")
st.info("Envie um documento de identificação com foto (RG, CNH, Passaporte) para verificação")

# Formulário de upload
with st.form("document_upload_form"):
    doc_type = st.selectbox(
        "Tipo de documento",
        options=["rg", "cnh", "cpf", "passport"],
        format_func=lambda x: {"rg": "RG", "cnh": "CNH", "cpf": "CPF", "passport": "Passaporte"}[x]
    )
    
    uploaded_file = st.file_uploader("Upload do documento", type=["jpg", "jpeg", "png", "pdf"])
    
    submit_doc = st.form_submit_button("Enviar documento")

# Captura de selfie para verificação
st.subheader("Captura de selfie")
st.info("Tire uma selfie para verificação de identidade")

# Webrtc para captura de selfie
col1, col2 = st.columns([2, 1])
with col1:
    webrtc_ctx = webrtc_streamer(
        key="selfie-capture",
        video_processor_factory=lambda: st.session_state.document_processor,
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True,
    )
    
with col2:
    if webrtc_ctx.video_processor:
        if st.button("Capturar Selfie"):
            st.session_state.document_processor.request_capture()
            st.info("Aguarde a captura...")

# Mostra selfie capturada
if st.session_state.document_processor.capture_done:
    st.session_state.selfie_captured = True
    st.success("Selfie capturada com sucesso!")
    
    # Converter para formato PIL e mostrar
    selfie_frame = st.session_state.document_processor.frame
    selfie_pil = Image.fromarray(cv2.cvtColor(selfie_frame, cv2.COLOR_BGR2RGB))
    
    st.image(selfie_pil, caption="Selfie capturada", width=300)
    
    # Preparar para envio
    buf = io.BytesIO()
    selfie_pil.save(buf, format='JPEG')
    selfie_bytes = buf.getvalue()

# Processar envio dos dados
if submit_doc and uploaded_file is not None:
    st.session_state.document_uploaded = True
    
    # Preparar arquivo para envio
    file_bytes = uploaded_file.getvalue()
    
    # Enviar documento
    files = {"file": (uploaded_file.name, file_bytes, f"image/{uploaded_file.type.split('/')[1]}")}
    response = make_api_request(
        f"/api/documents/upload?document_type={doc_type}",
        method="POST",
        files=files
    )
    
    if response and response.status_code in [200, 201]:
        st.success("Documento enviado com sucesso! Aguarde a verificação.")
    else:
        error_detail = "Erro desconhecido"
        if response:
            try:
                error_detail = response.json().get("detail", error_detail)
            except:
                pass
        st.error(f"Erro ao enviar documento: {error_detail}")

# Enviar selfie para verificação
if st.session_state.selfie_captured and st.session_state.document_uploaded:
    if st.button("Verificar Identidade"):
        st.info("Comparando selfie com documento...")
        
        # Aqui você enviaria a selfie para o endpoint de verificação
        # (Este endpoint precisaria ser implementado no backend)
        
        # Simulação de verificação bem-sucedida
        st.success("Verificação completada! Sua identidade será analisada em breve.")
        
        # Em um cenário real, enviaria a selfie para processamento pelo backend
        # files = {"selfie": ("selfie.jpg", selfie_bytes, "image/jpeg")}
        # response = make_api_request(
        #     f"/api/documents/verify-face/{document_id}",
        #     method="POST",
        #     files=files
        # )

# Instruções e dicas
with st.expander("Instruções para verificação de identidade"):
    st.write("""
    ### Como obter uma boa verificação:
    1. **Documento:**
       - Certifique-se de que o documento está bem iluminado
       - Todas as informações devem estar legíveis
       - Não corte nenhuma parte do documento
       
    2. **Selfie:**
       - Garanta boa iluminação
       - Olhe diretamente para a câmera
       - Não use óculos escuros, chapéus ou outros itens que cubram seu rosto
    """)

# Voltar para o Dashboard
if st.button("Voltar para o Dashboard"):
    st.session_state["current_page"] = "dashboard"
    st.experimental_rerun()