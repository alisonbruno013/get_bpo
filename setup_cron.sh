#!/bin/bash

# Script para configurar cron jobs automaticamente
# Execute: bash setup_cron.sh

echo "=========================================="
echo "Configuração de Cron Jobs para BPO"
echo "=========================================="

# Obtém o diretório atual do script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SCRIPT_PATH="$SCRIPT_DIR/scriptMain.py"
LOG_DIR="$SCRIPT_DIR/logs"
LOG_FILE="$LOG_DIR/cron.log"

# Cria diretório de logs se não existir
mkdir -p "$LOG_DIR"

# Encontra o Python
PYTHON_PATH=$(which python3)

if [ -z "$PYTHON_PATH" ]; then
    echo "❌ Erro: Python3 não encontrado!"
    exit 1
fi

echo "✅ Python encontrado: $PYTHON_PATH"
echo "✅ Script: $SCRIPT_PATH"
echo "✅ Logs: $LOG_FILE"

# Cria o arquivo de cron temporário
CRON_FILE=$(mktemp)

# Adiciona os jobs ao arquivo temporário
cat > "$CRON_FILE" << EOF
# Execução agendada BPO - 09:00
0 9 * * * $PYTHON_PATH $SCRIPT_PATH >> $LOG_FILE 2>&1

# Execução agendada BPO - 15:00
0 15 * * * $PYTHON_PATH $SCRIPT_PATH >> $LOG_FILE 2>&1

# Execução agendada BPO - 18:00
0 18 * * * $PYTHON_PATH $SCRIPT_PATH >> $LOG_FILE 2>&1

# Execução agendada BPO - 00:00
0 0 * * * $PYTHON_PATH $SCRIPT_PATH >> $LOG_FILE 2>&1
EOF

# Adiciona ao crontab
echo ""
echo "Adicionando jobs ao crontab..."
crontab "$CRON_FILE"

# Remove arquivo temporário
rm "$CRON_FILE"

echo "✅ Cron jobs configurados com sucesso!"
echo ""
echo "Jobs agendados:"
crontab -l | grep scriptMain.py
echo ""
echo "Para ver os logs:"
echo "  tail -f $LOG_FILE"
echo ""
echo "Para remover os jobs:"
echo "  crontab -e"
echo "  (delete as linhas relacionadas)"
