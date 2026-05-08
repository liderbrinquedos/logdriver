# LogDriver - Wiki do Projeto

## Visao Geral
Sistema de gerenciamento de entregas LogDriver. API FastAPI com autenticacao JWT, banco SQLite, frontend HTML/CSS/JS puro.

## Navegacao

### [[decisions]] — Architecture Decision Records
Decisoes arquiteturais importantes do projeto.

### [[architecture]] — Visao Arquitetural
Estrutura do sistema, fluxos de dados, componentes.

### [[patterns]] — Padroes de Codigo e Design
Convencoes e padroes utilizados no codigo.

### [[projects]] — Contexto por Projeto
Escopo, requisitos e estado atual de cada projeto/modulo.

### [[integrations]] — APIs e Servicos Externos
Integracoes com sistemas externos (LogDriver API, etc).

### [[snippets]] — Codigo Reutilizavel
Trechos de codigo uteis para uso frequente.

### [[templates]] — Templates para Novas Entradas
Modelos para criar novos documentos na wiki.

## Status Atual
- **Problema:** API retornando `nrunico: None` apesar de DB ter dados corretos
- **Causa suspeita:** Container rodando codigo stale (volume mount ausente no docker-compose)
- **Correcao aplicada:** Mapeamento de porta `8000:8000` e rebuild da imagem
