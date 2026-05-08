# Projeto LogDriver

## Escopo
Sistema de gerenciamento de entregas com:
- CRUD de entregas (deliveries)
- Importacao de planilhas (CSV/XLSX)
- Autenticacao de usuarios (admin/motorista)
- Dashboard com estatisticas
- Filtros por periodo, status, motorista, empresa

## Estado Atual
- MVP funcional com importacao e gestao basica
- Problema conhecido: `nrunico` retornando `null` via HTTP (suspeita de cache em container)
- Correcao em andamento: rebuild completo do container

## Funcionalidades Implementadas
- [x] Autenticacao JWT (login/logout)
- [x] Listagem de entregas com filtros
- [x] Criacao manual de entrega
- [x] Importacao via CSV/XLSX
- [x] Dashboard com estatisticas
- [x] CRUD de motoristas
- [x] Upload de comprovantes
- [x] Exportacao CSV
- [x] Validacao de duplicatas (NF+empresa)

## Funcionalidades Pendentes
- [ ] Webhook de notificacao
- [ ] Relatorios avancados
- [ ] App mobile (PWA)
