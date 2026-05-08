#!/usr/bin/env bash
# export-brain.sh - Exporta a estrutura .wiki + AGENTS.md + opencode config
# Uso: ./export-brain.sh [diretorio-projeto] [nome-do-pacote]
# Ex:  ./export-brain.sh /home/lider/project/sites/astralpro astralpro-brain

set -e

ORIGEM="${1:-.}"
NOME="${2:-brain-export}"
ORIGEM=$(cd "$ORIGEM" && pwd)
ARQUIVO="${NOME}.tar.gz"

echo "=== Exportando estrutura cerebral ==="
echo "Origem: $ORIGEM"
echo "Pacote: $ARQUIVO"

TMPDIR=$(mktemp -d)
PAKET_DIR="${TMPDIR}/${NOME}"
mkdir -p "$PAKET_DIR"

# Arquivos essenciais
echo ""
echo "Coletando arquivos..."

for item in ".wiki" "AGENTS.md" ".opencode/opencode.json" "SKILL.md"; do
    SRC="${ORIGEM}/${item}"
    if [ -e "$SRC" ]; then
        DEST_PARENT="${PAKET_DIR}/$(dirname "$item")"
        mkdir -p "$DEST_PARENT"
        cp -r "$SRC" "${DEST_PARENT}/"
        echo "  [OK] ${item}"
    else
        echo "  [..] ${item} (nao encontrado)"
    fi
done

# Instrucoes de importacao
cat > "${PAKET_DIR}/IMPORTAR.md" << 'EOF'
# Como usar este pacote em outro projeto

## Metodo rapido

```bash
# Dentro do diretorio do projeto alvo
tar -xzf brain-export.tar.gz
bash brain-export/import.sh
```

## Manual

```bash
# Dentro do diretorio do projeto alvo
cp -r brain-export/.wiki ./
cp brain-export/AGENTS.md ./
mkdir -p .opencode
cp brain-export/.opencode/opencode.json ./.opencode/
# Se existir:
cp brain-export/SKILL.md ./ 2>/dev/null || true
```

## Apos importar

1. Edite `.wiki/INDEX.md` -> atualize nome do projeto e contexto
2. Edite `AGENTS.md` -> ajuste regras se necessario
3. Edite `.opencode/opencode.json` -> instrucoes do seu projeto
4. Execute `opencode` no projeto para validar
EOF

# Script de importacao automatica
cat > "${PAKET_DIR}/import.sh" << 'IMPORT_EOF'
#!/usr/bin/env bash
# import.sh - Instala a estrutura cerebral no projeto atual
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DEST="$(pwd)"

echo "=== Importando estrutura cerebral ==="
echo "Destino: $DEST"

# .wiki
if [ -d "${SCRIPT_DIR}/.wiki" ]; then
    if [ -d "${DEST}/.wiki" ]; then
        echo "[!] .wiki/ ja existe -> mesclando sem sobrescrever"
        cp -rn "${SCRIPT_DIR}/.wiki" "${DEST}/" 2>/dev/null || true
    else
        cp -r "${SCRIPT_DIR}/.wiki" "${DEST}/"
        echo "[OK] .wiki/"
    fi
fi

# AGENTS.md
if [ -f "${SCRIPT_DIR}/AGENTS.md" ]; then
    if [ -f "${DEST}/AGENTS.md" ]; then
        echo "[!] AGENTS.md ja existe -> mantendo original"
    else
        cp "${SCRIPT_DIR}/AGENTS.md" "${DEST}/"
        echo "[OK] AGENTS.md"
    fi
fi

# opencode.json
if [ -f "${SCRIPT_DIR}/.opencode/opencode.json" ]; then
    mkdir -p "${DEST}/.opencode"
    if [ -f "${DEST}/.opencode/opencode.json" ]; then
        echo "[!] opencode.json ja existe -> mantendo original"
    else
        cp "${SCRIPT_DIR}/.opencode/opencode.json" "${DEST}/.opencode/"
        echo "[OK] .opencode/opencode.json"
    fi
fi

# SKILL.md
if [ -f "${SCRIPT_DIR}/SKILL.md" ]; then
    if [ -f "${DEST}/SKILL.md" ]; then
        echo "[!] SKILL.md ja existe -> mantendo original"
    else
        cp "${SCRIPT_DIR}/SKILL.md" "${DEST}/"
        echo "[OK] SKILL.md"
    fi
fi

echo ""
echo "=== Importacao concluida ==="
echo "Edite os arquivos abaixo para adaptar ao seu projeto:"
echo "  .wiki/INDEX.md"
echo "  AGENTS.md"
echo "  .opencode/opencode.json"
IMPORT_EOF

chmod +x "${PAKET_DIR}/import.sh"

# Gera tarball
tar -czf "$ARQUIVO" -C "$TMPDIR" "$NOME"
rm -rf "$TMPDIR"

TAM=$(du -sh "$ARQUIVO" | cut -f1)
echo ""
echo "=== Pronto ==="
echo "Arquivo: $(pwd)/$ARQUIVO ($TAM)"
echo ""
echo "Para usar em outro projeto:"
echo "  1. Copie $ARQUIVO para a maquina/pasta destino"
echo "  2. cd /projeto-alvo"
echo "  3. tar -xzf $ARQUIVO"
echo "  4. bash ${NOME}/import.sh"
