from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

router = APIRouter()

# Modelos Pydantic para validação
class Address(BaseModel):
    street: Optional[str] = None
    number: Optional[str] = None
    complement: Optional[str] = None
    neighborhood: Optional[str] = None
    city: str
    state: str
    country: str = "Brasil"
    zipcode: Optional[str] = None

class ProfileCreate(BaseModel):
    full_name: str
    cpf: str
    address: Address
    interests: List[str] = []
    furia_fan_since: Optional[str] = None
    attended_events: List[str] = []
    purchases: List[str] = []

class ProfileResponse(BaseModel):
    id: str
    user_id: str
    full_name: str
    address: Address
    interests: List[str]
    furia_fan_since: Optional[str] = None
    attended_events: List[str]
    purchases: List[str]

# Rotas para perfis
@router.post("/", response_model=ProfileResponse)
async def create_profile(profile: ProfileCreate, request: Request):
    db = request.state.db
    
    # Na versão completa, verificar se o usuário está autenticado
    # E obter o user_id do token
    # Por enquanto, usar um ID fictício
    user_id = "user123"  # Este deve vir da autenticação
    
    # Verificar se perfil já existe para este usuário
    existing_profile = db.profiles.find_one({"user_id": user_id})
    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Perfil já existe para este usuário"
        )
    
    # Criar novo perfil
    profile_data = profile.dict()
    profile_data["user_id"] = user_id
    profile_data["created_at"] = datetime.utcnow()
    
    result = db.profiles.insert_one(profile_data)
    
    # Retornar dados do perfil criado
    created_profile = db.profiles.find_one({"_id": result.inserted_id})
    created_profile["id"] = str(created_profile["_id"])
    return created_profile

@router.get("/{user_id}", response_model=ProfileResponse)
async def get_profile(user_id: str, request: Request):
    db = request.state.db
    
    # Na versão completa, verificar se o usuário está autenticado
    # E só pode acessar seu próprio perfil (ou ser admin)
    
    profile = db.profiles.find_one({"user_id": user_id})
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil não encontrado"
        )
    
    profile["id"] = str(profile["_id"])
    return profile

@router.put("/{user_id}", response_model=ProfileResponse)
async def update_profile(user_id: str, profile: ProfileCreate, request: Request):
    db = request.state.db
    
    # Na versão completa, verificar se o usuário está autenticado
    # E só pode atualizar seu próprio perfil (ou ser admin)
    
    existing_profile = db.profiles.find_one({"user_id": user_id})
    if not existing_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil não encontrado"
        )
    
    # Atualizar perfil
    profile_data = profile.dict()
    profile_data["updated_at"] = datetime.utcnow()
    
    db.profiles.update_one(
        {"user_id": user_id},
        {"$set": profile_data}
    )
    
    # Retornar perfil atualizado
    updated_profile = db.profiles.find_one({"user_id": user_id})
    updated_profile["id"] = str(updated_profile["_id"])
    return updated_profile