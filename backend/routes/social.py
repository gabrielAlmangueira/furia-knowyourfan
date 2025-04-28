from fastapi import APIRouter, HTTPException, status, Request
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

router = APIRouter()

# Modelos Pydantic para validação
class SocialAccountCreate(BaseModel):
    platform: str
    username: str
    profile_url: str

class SocialAccountResponse(BaseModel):
    id: str
    user_id: str
    platform: str
    username: str
    profile_url: str
    relevance_score: Optional[float] = None
    connected_at: datetime

# Rotas para contas sociais
@router.post("/", response_model=SocialAccountResponse)
async def connect_social_account(social: SocialAccountCreate, request: Request):
    db = request.state.db
    
    # Na versão completa, verificar se o usuário está autenticado
    # E obter o user_id do token
    user_id = "user123"  # Este deve vir da autenticação
    
    # Verificar plataforma
    allowed_platforms = ["twitter", "instagram", "facebook", "discord", "twitch"]
    if social.platform.lower() not in allowed_platforms:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Plataforma não suportada. Permitidas: {', '.join(allowed_platforms)}"
        )
    
    # Verificar se já existe conta dessa plataforma para o usuário
    existing = db.social_accounts.find_one({
        "user_id": user_id,
        "platform": social.platform
    })
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Já existe uma conta {social.platform} conectada para este usuário"
        )
    
    # Criar nova conta social
    social_data = social.dict()
    social_data["user_id"] = user_id
    social_data["connected_at"] = datetime.utcnow()
    social_data["relevance_score"] = 0.0  # Inicialmente sem pontuação
    
    # Na versão completa, fazer análise de relevância baseada no nome de usuário
    # ou no perfil fornecido (utilizando serviço de IA)
    
    result = db.social_accounts.insert_one(social_data)
    
    # Retornar conta social criada
    created = db.social_accounts.find_one({"_id": result.inserted_id})
    created["id"] = str(created["_id"])
    return created

@router.get("/user/{user_id}", response_model=List[SocialAccountResponse])
async def get_user_social_accounts(user_id: str, request: Request):
    db = request.state.db
    
    # Na versão completa, verificar se o usuário está autenticado
    # E só pode acessar suas próprias contas
    
    # Buscar contas do usuário
    accounts = list(db.social_accounts.find({"user_id": user_id}))
    
    # Formatar para retorno
    for account in accounts:
        account["id"] = str(account["_id"])
    
    return accounts

@router.delete("/{account_id}")
async def delete_social_account(account_id: str, request: Request):
    db = request.state.db
    
    # Na versão completa, verificar se o usuário está autenticado
    # E só pode deletar suas próprias contas
    
    # Verificar se conta existe
    account = db.social_accounts.find_one({"_id": account_id})
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conta social não encontrada"
        )
    
    # Deletar conta
    db.social_accounts.delete_one({"_id": account_id})
    
    return {"status": "success", "message": "Conta social desconectada com sucesso"}

@router.post("/analyze/{account_id}")
async def analyze_social_account(account_id: str, request: Request):
    db = request.state.db
    
    # Na versão completa, verificar se o usuário está autenticado
    # E só pode analisar suas próprias contas
    
    # Verificar se conta existe
    account = db.social_accounts.find_one({"_id": account_id})
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conta social não encontrada"
        )
    
    # Na versão completa, chamar serviço de análise de relevância
    # Aqui, apenas simulamos a análise
    relevance_score = 0.75  # Valor simulado entre 0 e 1
    
    # Atualizar pontuação
    db.social_accounts.update_one(
        {"_id": account_id},
        {"$set": {
            "relevance_score": relevance_score,
            "analyzed_at": datetime.utcnow()
        }}
    )
    
    return {
        "status": "success", 
        "message": "Análise concluída", 
        "relevance_score": relevance_score
    }