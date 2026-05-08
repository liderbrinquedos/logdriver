# Arquitetura do LogDriver

## Stack
- **Backend:** FastAPI + SQLAlchemy + SQLite
- **Autenticacao:** JWT (python-jose)
- **Frontend:** HTML/CSS/JS puro (LiderLog.html)
- **Containerizacao:** Docker + docker-compose
- **Servidor:** uvicorn (backend), nginx (frontend)

## Estrutura de Diretorios
```
/
├── backend/
│   ├── main.py          # FastAPI app com todos os endpoints
│   ├── models.py        # Modelos SQLAlchemy (Delivery, User)
│   ├── schemas.py       # Pydantic schemas
│   ├── auth_utils.py    # Utilitarios de autenticacao JWT
│   ├── database.py      # Configuracao do banco SQLite
│   ├── requirements.txt # Dependencias Python
│   └── Dockerfile       # Build do backend
├── frontend/
│   └── LiderLog.html    # SPA frontend (single file)
├── docker-compose.yml   # Orquestracao dos servicos
├── AGENTS.md            # Instrucoes para opencode/subagentes
├── export-brain.sh      # Script de exportacao da estrutura cerebral
└── .wiki/               # Documentacao do projeto
```

## Fluxo de Dados
1. Usuario faz login → recebe JWT
2. Frontend autentica requisicoes com Bearer token
3. Backend valida token → processa request → retorna JSON
4. Importacao de planilhas: CSV/XLSX → validacao → SQLite

## Portas
- Backend API: 8000 (container) → 8000 (host)
- Frontend: 80 (container) → 8021 (host)
