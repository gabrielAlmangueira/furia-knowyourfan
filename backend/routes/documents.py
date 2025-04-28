from fastapi import APIRouter, HTTPException, status, Request, File, UploadFile
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
import os
import shutil
from pathlib import Path

router = APIRouter()

# Modelos Pydantic para validação
class DocumentResponse(BaseModel):
    id: str
    user_id: str
    document_type: str
    file_path: str
    verification_status: str
    upload_date: datetime

# Rotas para documentos
@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    document_type: str,
    file: UploadFile = File(...),
    request: Request = None
):
    db = request.state.db
    
    # Na versão completa, verificar se o usuário está autenticado
    # E obter o user_id do token JWT
    user_id = "user123"  # Este deve vir da autenticação
    
    # Verificar tipo de documento
    allowed_types = ["rg", "cnh", "cpf", "passport"]
    if document_type.lower() not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de documento inválido. Permitidos: {', '.join(allowed_types)}"
        )
    
    # Verificar tipo de arquivo
    allowed_extensions = [".jpg", ".jpeg", ".png", ".pdf"]
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Formato de arquivo inválido. Permitidos: {', '.join(allowed_extensions)}"
        )
    
    # Criar pasta de uploads se não existir
    upload_dir = Path("uploads")
    user_dir = upload_dir / user_id
    user_dir.mkdir(parents=True, exist_ok=True)
    
    # Salvar arquivo
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    safe_filename = f"{document_type}_{timestamp}{file_extension}"
    file_path = user_dir / safe_filename
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Salvar informações no banco de dados
    document_data = {
        "user_id": user_id,
        "document_type": document_type,
        "file_path": str(file_path),
        "upload_date": datetime.utcnow(),
        "verification_status": "pending"  # Inicialmente pendente
    }
    
    result = db.documents.insert_one(document_data)
    
    # Na versão completa, iniciar processo de verificação assíncrono
    # Aqui, apenas simulamos a resposta
    
    # Retornar documento criado
    created_doc = db.documents.find_one({"_id": result.inserted_id})
    created_doc["id"] = str(created_doc["_id"])
    return created_doc

@router.get("/status/{user_id}", response_model=List[DocumentResponse])
async def get_documents_status(user_id: str, request: Request):
    db = request.state.db
    
    # Na versão completa, verificar se o usuário está autenticado
    # E só pode acessar seus próprios documentos
    
    # Buscar documentos do usuário
    documents = list(db.documents.find({"user_id": user_id}))
    
    # Formatar para retorno
    for doc in documents:
        doc["id"] = str(doc["_id"])
    
    return documents

@router.post("/verify/{document_id}")
async def verify_document(document_id: str, request: Request):
    db = request.state.db
    
    # Na versão completa, verificar se o usuário está autenticado
    # E se tem permissão para verificar documentos (admin)
    
    # Buscar documento
    document = db.documents.find_one({"_id": document_id})
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Documento não encontrado"
        )
    
    # Na versão completa, chamar serviço de IA para verificar documento
    # Aqui, apenas simulamos a verificação
    
    # Atualizar status
    db.documents.update_one(
        {"_id": document_id},
        {"$set": {
            "verification_status": "verified",
            "verified_at": datetime.utcnow()
        }}
    )
    
    return {"status": "success", "message": "Documento verificado com sucesso"}