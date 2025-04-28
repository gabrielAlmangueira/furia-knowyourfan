from fastapi import APIRouter, HTTPException, status, Request, File, UploadFile
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
import shutil
from pathlib import Path

router = APIRouter()

# Modelos Pydantic para validação
class EsportsProfileCreate(BaseModel):
    platform: str
    username: str
    profile_url: str

class EsportsProfileResponse(BaseModel):
    id: str
    user_id: str
    platform: str
    username: str
    profile_url: str
    verified: bool
    created_at: datetime

# Rotas para perfis de e-sports
@router.post("/", response_model=EsportsProfileResponse)
async def create_esports_profile(profile: EsportsProfileCreate, request: Request):
    db = request.state.db
    
    # Na versão completa, verificar se o usuário está autenticado
    # E obter o user_id do token
    user_id = "user123"  # Este deve vir da autenticação
    
    # Verificar plataforma
    allowed_platforms = ["steam", "faceit", "battlefy", "riot", "epic"]
    if profile.platform.lower() not in allowed_platforms:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Plataforma não suportada. Permitidas: {', '.join(allowed_platforms)}"
        )
    
    # Verificar se já existe perfil dessa plataforma para o usuário
    existing = db.esports_profiles.find_one({
        "user_id": user_id,
        "platform": profile.platform
    })
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Já existe um perfil {profile.platform} registrado para este usuário"
        )
    
    # Criar novo perfil
    profile_data = profile.dict()
    profile_data["user_id"] = user_id
    profile_data["created_at"] = datetime.utcnow()
    profile_data["verified"] = False  # Inicialmente não verificado
    
    result = db.esports_profiles.insert_one(profile_data)
    
    # Retornar perfil criado
    created = db.esports_profiles.find_one({"_id": result.inserted_id})
    created["id"] = str(created["_id"])
    return created

@router.get("/user/{user_id}", response_model=List[EsportsProfileResponse])
async def get_user_esports_profiles(user_id: str, request: Request):
    db = request.state.db
    
    # Na versão completa, verificar se o usuário está autenticado
    # E só pode acessar seus próprios perfis
    
    # Buscar perfis do usuário
    profiles = list(db.esports_profiles.find({"user_id": user_id}))
    
    # Formatar para retorno
    for profile in profiles:
        profile["id"] = str(profile["_id"])
    
    return profiles

@router.post("/verify/{profile_id}")
async def verify_esports_profile(
    profile_id: str, 
    screenshot: UploadFile = File(...),
    request: Request = None
):
    db = request.state.db
    
    # Na versão completa, verificar se o usuário está autenticado
    # E só pode verificar seus próprios perfis
    
    # Verificar se o perfil existe
    profile = db.esports_profiles.find_one({"_id": profile_id})
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil não encontrado"
        )
    
    # Verificar tipo de arquivo
    allowed_extensions = [".jpg", ".jpeg", ".png"]
    file_extension = Path(screenshot.filename).suffix.lower()
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Formato de arquivo inválido. Permitidos: {', '.join(allowed_extensions)}"
        )
    
    # Criar pasta para screenshots se não existir
    user_id = profile["user_id"]
    upload_dir = Path("uploads") / "screenshots" / user_id
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Salvar screenshot
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    safe_filename = f"{profile['platform']}_{timestamp}{file_extension}"
    file_path = upload_dir / safe_filename
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(screenshot.file, buffer)
    
    # Na versão completa, chamar serviço de IA para verificar a screenshot
    # e confirmar que é um perfil válido/relevante
    
    # Aqui, apenas simulamos a verificação
    verification_result = True  # Simulando verificação bem-sucedida
    
    # Atualizar perfil
    db.esports_profiles.update_one(
        {"_id": profile_id},
        {"$set": {
            "verified": verification_result,
            "screenshot_path": str(file_path),
            "verified_at": datetime.utcnow()
        }}
    )
    
    return {
        "status": "success", 
        "message": "Perfil verificado com sucesso" if verification_result else "Falha na verificação",
        "verified": verification_result
    }