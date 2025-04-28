from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import pymongo
import os
from datetime import datetime, timedelta

# Importações internas serão adicionadas à medida que os módulos forem criados
from routes import users, profiles, documents, social, esports

# Configuração da aplicação FastAPI
app = FastAPI(
    title="FURIA Know Your Fan API",
    description="API para coleta e análise de dados de fãs da FURIA",
    version="0.1.0"
)

# Configuração de CORS para permitir requisições do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar o domínio do frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Conexão com o MongoDB
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
client = pymongo.MongoClient(MONGODB_URI)
db = client["furia_kyf"]

# Disponibilizando o banco de dados para os endpoints
@app.middleware("http")
async def add_db_to_request(request, call_next):
    request.state.db = db
    response = await call_next(request)
    return response

# Rota de status para verificar se a API está funcionando
@app.get("/", tags=["Status"])
async def read_root():
    return {
        "status": "online",
        "message": "FURIA Know Your Fan API está funcionando",
        "timestamp": datetime.now().isoformat()
    }

# Incluindo os routers dos diversos módulos
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(profiles.router, prefix="/api/profiles", tags=["Profiles"])
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(social.router, prefix="/api/social", tags=["Social"])
app.include_router(esports.router, prefix="/api/esports", tags=["Esports"])

# Função para inicialização
@app.on_event("startup")
async def startup():
    # Criar índices necessários
    db.users.create_index("email", unique=True)
    db.users.create_index("username", unique=True)
    print("API inicializada com sucesso!")

# Função para encerramento
@app.on_event("shutdown")
async def shutdown():
    client.close()
    print("Conexão com o banco de dados fechada.")