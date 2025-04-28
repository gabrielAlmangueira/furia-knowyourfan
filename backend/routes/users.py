from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
import os

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Modelos Pydantic para validação
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    created_at: datetime

# Funções de autenticação
def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire})
    
    # Na prática, armazenar este segredo em uma variável de ambiente
    secret_key = os.getenv("JWT_SECRET", "your_secret_key")
    
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm="HS256")
    return encoded_jwt

# Rotas para usuários
@router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate, request: Request):
    db = request.state.db
    
    # Verificar se usuário já existe
    if db.users.find_one({"email": user.email}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado"
        )
    
    if db.users.find_one({"username": user.username}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nome de usuário já existe"
        )
    
    # Criar novo usuário
    user_data = {
        "username": user.username,
        "email": user.email,
        "password_hash": get_password_hash(user.password),
        "created_at": datetime.utcnow()
    }
    
    result = db.users.insert_one(user_data)
    
    # Retornar dados do usuário sem a senha
    created_user = db.users.find_one({"_id": result.inserted_id})
    return {
        "id": str(created_user["_id"]),
        "username": created_user["username"],
        "email": created_user["email"],
        "created_at": created_user["created_at"]
    }

@router.post("/login")
async def login_user(user: UserLogin, request: Request):
    db = request.state.db
    
    # Verificar usuário
    db_user = db.users.find_one({"username": user.username})
    if not db_user or not verify_password(user.password, db_user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Gerar token de acesso
    access_token = create_access_token(
        data={"sub": str(db_user["_id"]), "username": db_user["username"]}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": str(db_user["_id"]),
        "username": db_user["username"]
    }

@router.get("/me", response_model=UserResponse)
async def read_users_me(request: Request):
    # Esta rota precisará de um middleware de autenticação
    # Por enquanto, retorna um erro
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Rota ainda não implementada completamente"
    )