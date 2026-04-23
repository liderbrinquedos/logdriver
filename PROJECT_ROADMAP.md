# Roadmap do Projeto LiderLog

Este documento contém o planejamento de recursos futuros aprovados para o sistema.

## 1. Fase: Filtros de Performance (Pendente)
**Objetivo:** Garantir que o app permaneça rápido mesmo com milhares de registros.

### Tarefas Técnicas:
- [ ] **Backend:** Atualizar a rota `GET /api/deliveries` para aceitar `start_date`, `end_date` e `status`.
- [ ] **Backend:** Implementar índices no banco de dados para buscas rápidas.
- [ ] **Frontend:** Adicionar barra de filtros (Status e Período) no topo da aba de entregas.
- [ ] **Frontend:** Implementar carregamento sob demanda (Server-side filtering).

---

## 2. Fase: Agendamento de Entregas (Pendente)
**Objetivo:** Gerenciar entregas futuras em CDs com data e hora marcada.

### Tarefas Técnicas:
- [ ] **Modelo:** Adicionar coluna `scheduled_at` no banco de dados.
- [ ] **Importação:** Atualizar o leitor de Excel para processar a coluna de agendamento.
- [ ] **Cadastro:** Incluir seletor de data/hora no formulário de "Novo Registro".
- [ ] **Interface:** Exibir selo visual (📅) em entregas agendadas na lista principal.

---

## Recursos em Discussão

### A. Gestão de Documentos Cloud
- [ ] **Nomenclatura e Conversão para PDF:** 
    - **App:** Mantém JPG (Original) para visualização rápida no celular.
    - **Exportação/Cloud:** Converte para PDF otimizado (tons de cinza/contraste) no momento do envio para o OneDrive.
    - **Nomenclatura Sugerida:** `NF_CLIENTE_DATA.pdf`.
- [ ] **Sincronização Diária com OneDrive:** Script automatizado (Cron job) para enviar os documentos da pasta `uploads/` para o OneDrive uma vez ao dia.

### B. Funcionalidades Extras
- [ ] **Geolocalização:** Captura de GPS no ato da entrega (Prova de entrega).
- [ ] **Leitura de Código de Barras:** Usar a câmera para abrir a entrega instantaneamente.
- [ ] **Dashboard Visual:** Gráficos de desempenho e volume de entregas.
