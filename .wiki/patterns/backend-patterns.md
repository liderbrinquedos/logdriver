# Padroes do Backend

## Endpoints
- Todos os endpoints sao definidos como funcoes no proprio arquivo `main.py` (sem routers separados)
- Prefixo `/api/` para todos os endpoints
- Retornos em JSON com serializacao manual (dict inline)

## Autenticacao
- JWT via OAuth2PasswordBearer
- Token armazenado no localStorage do frontend
- Endpoints protegidos com `Depends(get_current_user)`

## Banco de Dados
- SQLite via SQLAlchemy ORM
- Sessao gerenciada por `get_db()` dependency
- Modelos em `models.py`, schemas em `schemas.py`

## Tratamento de Erros
- Erros de autenticacao: 401 Unauthorized
- Erros de permissao: 403 Forbidden
- Erros de validacao: 422 Unprocessable Entity (FastAPI padrao)
- Erros de recurso: 404 Not Found

## Validacao de Duplicatas (Importacao)
- Bloqueia NF+empresa duplicados na criacao manual
- Ignora/skipa duplicatas durante importacao em lote
- Log de warnings para linhas duplicadas ignoradas
