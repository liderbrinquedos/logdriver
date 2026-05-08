# ADR-001: Correcao do campo nrunico na API de Deliveries

## Contexto
O campo `nrunico` estava sendo salvo corretamente no banco de dados (via importacao de planilhas), mas retornava `null` nas respostas da API.

## Decisao
1. Substituir o uso de `format_delivery_response(d)` por um dict inline no endpoint `list_deliveries` para garantir que `nrunico` seja incluido na resposta
2. Adicionar mapeamento de porta `8000:8000` no `docker-compose.yml` para permitir acesso direto a API
3. Alterar validacao de duplicatas para usar `nrunico` como criterio principal (unico global do LogDriver)

## Consequencias
- Positivas: 
  - Campo `nrunico` agora eh retornado corretamente
  - Duplicatas sao detectadas pelo `nrunico` (mais preciso que NF+empresa)
  - Criacao manual passou a aceitar `nrunico` como campo opcional
- Negativas: Duplicacao de logica de serializacao (inline dict + format_delivery_response)

## Status
Implementado.

## Referencias
- `backend/main.py` linha ~254: inline dict em list_deliveries
- `backend/main.py` linha ~320: validacao por nrunico na importacao
- `backend/main.py` linha ~398: validacao por nrunico na criacao manual
- `docker-compose.yml` linha 6: mapeamento de porta adicionado
