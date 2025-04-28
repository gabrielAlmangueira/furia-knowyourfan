# FURIA - Know Your Fan (KYF)

![FURIA Logo](https://upload.wikimedia.org/wikipedia/pt/f/f9/Furia_Esports_logo.png)

## Descrição

**Know Your Fan** é uma aplicação desenvolvida para a FURIA Esports que permite coletar informações sobre os fãs, validar suas identidades e analisar seu engajamento. 

Esta solução visa ajudar a FURIA a conhecer melhor seu público e oferecer experiências e serviços personalizados, fortalecendo a relação entre a organização e seus fãs.

## Funcionalidades

- **Coleta de dados básicos**: Informações pessoais, endereço, interesses e histórico como fã
- **Verificação de identidade**: Upload de documentos e validação usando reconhecimento facial
- **Vinculação de redes sociais**: Conexão e análise de perfis sociais
- **Perfis de e-sports**: Vinculação de contas em plataformas de jogos
- **Análise de engajamento**: Pontuação e segmentação de fãs

## Tecnologias

### Backend
- **Python** com **FastAPI**
- **MongoDB** para armazenamento de dados
- **Face Recognition** para verificação de identidade
- **Transformers** para análise de conteúdo

### Frontend
- **Streamlit** para interface interativa
- **Plotly** para visualizações
- **Streamlit-WebRTC** para captura de câmera

### Infraestrutura
- **Docker** para containerização
- **Docker Compose** para orquestração local

## Instalação e Execução

### Pré-requisitos
- Docker e Docker Compose instalados
- Git

### Passos para instalação

1. Clone o repositório:
```
git clone https://github.com/seu-usuario/furia-knowyourfan.git
cd furia-knowyourfan
```

2. Inicie os containers:
```
docker-compose up -d
```

3. Acesse a aplicação:
   - Frontend: http://localhost:8501
   - API Backend: http://localhost:8000/docs

## Estrutura do Projeto

```
furia-knowyourfan/
├── README.md
├── docker-compose.yml
├── frontend/
│   ├── Dockerfile
│   ├── app.py
│   ├── requirements.txt
│   └── pages/
│       ├── profile.py
│       ├── documents.py
│       ├── social.py
│       └── esports.py
├── backend/
│   ├── Dockerfile
│   ├── main.py
│   ├── requirements.txt
│   ├── models/
│   ├── routes/
│   └── services/
├── ai/
│   ├── face_recognition.py
│   └── content_analyzer.py
└── uploads/
```

## Uso da Aplicação

1. Crie uma conta ou faça login
2. Preencha seu perfil com informações básicas
3. Faça upload de um documento para verificação
4. Vincule suas redes sociais e perfis de e-sports
5. Visualize seu dashboard personalizado


## Autores

- Gabriel de Almeida - [gabrielam1040@outlook.com](mailto:gabrielam1040@outlook.com)

