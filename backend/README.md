# LiderLog Backend

Backend para o sistema de controle de entregas LiderLog.

## Tecnologias

- **FastAPI** - Framework web moderno e rápido
- **SQLAlchemy** - ORM para banco de dados
- **SQLite** - Banco de dados leve (pode ser substituído por PostgreSQL/MySQL)
- **Pydantic** - Validação de dados

## Instalação

1. Crie um ambiente virtual:
```bash
cd backend
python -m venv venv
```

2. Ative o ambiente virtual:
```bash
# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Execução

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

O backend estará disponível em: `http://localhost:8000`

## API Endpoints

- `GET /api/health` - Health check
- `GET /api/stats` - Estatísticas de entregas
- `GET /api/deliveries` - Listar todas as entregas
- `POST /api/deliveries` - Criar nova entrega
- `GET /api/deliveries/{id}` - Buscar entrega por ID
- `PATCH /api/deliveries/{id}/status` - Atualizar status da entrega
- `PATCH /api/deliveries/{id}/confirm` - Confirmar entrega com canhoto
- `DELETE /api/deliveries/{id}` - Deletar entrega

## Documentação da API

Após iniciar o servidor, acesse:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Estrutura do Projeto

```
backend/
├── database.py    # Configuração do banco de dados
├── models.py      # Modelos SQLAlchemy
├── schemas.py     # Schemas Pydantic para validação
├── main.py        # Aplicativo FastAPI e rotas
└── requirements.txt
```

## Desenvolvimento

Para usar outro banco de dados (PostgreSQL, MySQL), altere a `SQLALCHEMY_DATABASE_URL` no arquivo `database.py`.
