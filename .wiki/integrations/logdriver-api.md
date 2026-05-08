# Integracao com API LogDriver

## Endpoints Principais

### Autenticacao
- `POST /api/auth/login` — Login (retorna JWT)
- `POST /api/auth/register` — Registro de usuario

### Deliveries
- `GET /api/deliveries` — Lista entregas (com filtros)
- `POST /api/deliveries` — Cria nova entrega
- `PUT /api/deliveries/{id}` — Atualiza entrega
- `DELETE /api/deliveries/{id}` — Remove entrega
- `POST /api/deliveries/import` — Importa planilha

### Motoristas
- `GET /api/drivers` — Lista motoristas
- `POST /api/drivers` — Cria motorista

### Estatisticas
- `GET /api/stats` — Dashboard stats

## Parametros de Filtro (GET /api/deliveries)
| Parametro | Tipo | Descricao |
|-----------|------|-----------|
| period | string | today, week, month, all |
| status | string | pendente, entregue, etc |
| order | string | asc, desc |
| limit | int | max resultados |
| driver | string | filtro por motorista |
| company | string | filtro por empresa |
