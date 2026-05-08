# AGENTS.md - Instrucoes para opencode e Subagentes

## Regra Principal

Antes de qualquer tarefa, consulte `.wiki/INDEX.md` para entender o contexto do projeto, padroes existentes e decisoes arquiteturais registradas.

## Workflow Obrigatorio

### 1. Antes de Codar
- Leia `.wiki/INDEX.md` para contexto geral
- Consulte `.wiki/patterns/` para seguir padroes estabelecidos
- Consulte `.wiki/decisions/` para nao repetir decisoes ja tomadas

### 2. Durante o Desenvolvimento
- Siga os padroes documentados em `.wiki/patterns/`
- Use snippets de `.wiki/snippets/` quando disponiveis
- Consulte `.wiki/integrations/` antes de criar novas integracoes

### 3. Apos Tomar Decisoes Importantes
- Crie um ADR em `.wiki/decisions/` usando `.wiki/templates/decision-template.md`
- Atualize `.wiki/INDEX.md` com o novo link
- Referencie o ADR no codigo com comentario: `// ADR-XXX: motivo`

### 4. Ao Criar Novos Padroes
- Documente em `.wiki/patterns/` usando `.wiki/templates/pattern-template.md`
- Atualize `.wiki/INDEX.md`

## Estrutura da Wiki

```
.wiki/
├── INDEX.md              ← SEMPRE consultar primeiro
├── decisions/            ← Architecture Decision Records
├── architecture/         ← Visao arquitetural
├── patterns/             ← Padroes de codigo e design
├── projects/             ← Contexto por projeto
├── integrations/         ← APIs e servicos externos
├── snippets/             ← Codigo reutilizavel
└── templates/            ← Templates para novas entradas
```

## Para Subagentes

- Voce tem acesso total a `.wiki/`
- Use o conteudo como contexto para decisoes tecnicas
- Se informacao nao existir na wiki, documente ao final da tarefa
- Nunca ignore um ADR existente sem justificativa

## Convencoes

- Links entre paginas usam `[[nome-do-arquivo]]` (sem extensao .md)
- ADRs sao numerados: `001-titulo.md`, `002-titulo.md`
- Tudo em markdown, sem emojis
- Idioma: portugues
