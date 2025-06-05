#!/bin/bash
# Script para corrigir problemas comuns com a configuração das VMs
# /home/istec/projeto_final/satellite/fix_common_issues.sh

echo "=========================================="
echo "AJUSTE DE CONFIGURAÇÃO DAS VMs"
echo "=========================================="

# Definindo as variáveis
GS_IP="192.168.1.96"
GS_USER="groundstation"
GS_LOGS_DIR="/home/groundstation/projeto_final/GS/logs"

# 1. Verificar ping para VMGS
echo -e "\n[1/6] Verificando conexão com VMGS (${GS_IP})..."
if ping -c 2 ${GS_IP} > /dev/null; then
    echo "✅ VMGS acessível via ping"
else
    echo "❌ ERRO: Não foi possível conectar à VMGS via ping"
    echo "   Verifique se a VM está ligada e se o IP está correto"
    echo "   Execute 'ip addr' para verificar sua configuração de rede"
fi

# 2. Corrigir as chaves SSH
echo -e "\n[2/6] Corrigindo configuração SSH..."
# Remover chaves antigas
ssh-keygen -f "$HOME/.ssh/known_hosts" -R "${GS_IP}" 2>/dev/null

# Configurar SSH para não verificar chaves
mkdir -p ~/.ssh
cat > ~/.ssh/config << EOF
Host ${GS_IP} vmgs groundstation
    HostName ${GS_IP}
    User ${GS_USER}
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
EOF

chmod 600 ~/.ssh/config
echo "✅ Configuração SSH atualizada"

# 3. Verificar configuração do aplicativo
echo -e "\n[3/6] Verificando configuração do app.py..."
APP_PATH="/home/istec/projeto_final/GS/dashboard/app.py"

if [ -f "$APP_PATH" ]; then
    LOGS_PATH=$(grep -o "LOGS_DIR = Path(\"[^\"]*\")" "$APP_PATH" | cut -d'"' -f2)
    echo "   Dashboard configurado para ler logs em: $LOGS_PATH"
    
    # Corrigir caminho se estiver incorreto
    if [ "$LOGS_PATH" != "/home/groundstation/projeto_final/GS/logs" ]; then
        echo "   ⚠️ Caminho incorreto detectado no app.py. Corrigindo..."
        sed -i 's|LOGS_DIR = Path("[^"]*")|LOGS_DIR = Path("/home/groundstation/projeto_final/GS/logs")|' "$APP_PATH"
        echo "   ✅ Caminho corrigido para /home/groundstation/projeto_final/GS/logs"
    else
        echo "   ✅ Caminho do dashboard está correto"
    fi
else
    echo "❌ ERRO: Arquivo app.py não encontrado em $APP_PATH"
fi

# 4. Verificar estrutura de diretórios na VMGS
echo -e "\n[4/6] Criando estrutura de diretórios na VMGS..."
if ssh -o ConnectTimeout=5 ${GS_USER}@${GS_IP} "mkdir -p ${GS_LOGS_DIR}/{adcs,power,thermal,communication,system}" 2>/dev/null; then
    ssh ${GS_USER}@${GS_IP} "chmod -R 777 ${GS_LOGS_DIR}" 2>/dev/null
    echo "✅ Estrutura de diretórios criada na VMGS"
else
    echo "❌ ERRO: Não foi possível criar diretórios na VMGS."
    echo "   Pode ser um problema de permissão ou usuário inexistente."
fi

# 5. Testar escrita de log
echo -e "\n[5/6] Testando escrita de arquivo de log..."
TEST_DATA="{\"timestamp\":\"$(date -Iseconds)\",\"test\":true}"
if ssh ${GS_USER}@${GS_IP} "echo '[${TEST_DATA}]' > ${GS_LOGS_DIR}/system/test.json" 2>/dev/null; then
    echo "✅ Arquivo de teste escrito com sucesso"
    ssh ${GS_USER}@${GS_IP} "cat ${GS_LOGS_DIR}/system/test.json"
else
    echo "❌ ERRO: Não foi possível escrever arquivo de teste"
fi

# 6. Verificar script de processamento QEMU
echo -e "\n[6/7] Verificando script de processamento QEMU..."
PROC_PATH="/home/istec/projeto_final/satellite/process_qemu_output.py"

if [ -f "$PROC_PATH" ]; then
    # Verificar se o módulo random está importado
    if grep -q "import random" "$PROC_PATH"; then
        echo "✅ Módulo random já está importado no script de processamento"
    else
        echo "⚠️ Módulo random não encontrado no script de processamento"
        echo "   Adicionando importação automaticamente..."
        sed -i '1,20s/import os/import os\nimport random/' "$PROC_PATH"
        if grep -q "import random" "$PROC_PATH"; then
            echo "✅ Módulo random adicionado com sucesso"
        else
            echo "❌ Falha ao adicionar módulo random"
        fi
    fi
    
    # Verificar se o usuário está configurado corretamente
    if grep -q "GS_USER = \"$GS_USER\"" "$PROC_PATH"; then
        echo "✅ Usuário da GS configurado corretamente"
    else
        echo "⚠️ Usuário da GS pode estar incorreto"
        echo "   Atualizando..."
        sed -i "s/GS_IP = \"192.168.1.96\"/GS_IP = \"192.168.1.96\"\nGS_USER = \"$GS_USER\"/" "$PROC_PATH"
    fi
else
    echo "❌ ERRO: Script de processamento não encontrado em $PROC_PATH"
fi

# 7. Verificar script de simulação
echo -e "\n[7/8] Verificando script de simulação..."
SIM_PATH="/home/istec/projeto_final/satellite/simulate_logs.py"

if [ -f "$SIM_PATH" ]; then
    SIM_GS_IP=$(grep -o "GS_IP = \"[^\"]*\"" "$SIM_PATH" | cut -d'"' -f2)
    SIM_LOGS_DIR=$(grep -o "GS_LOGS_DIR = \"[^\"]*\"" "$SIM_PATH" | cut -d'"' -f2)
    
    echo "   Script de simulação configurado para:"
    echo "   - IP da VMGS: $SIM_GS_IP"
    echo "   - Diretório de logs: $SIM_LOGS_DIR"
    
    # Verificar se os valores estão corretos
    if [ "$SIM_GS_IP" != "$GS_IP" ]; then
        echo "⚠️ AVISO: O IP da VMGS no script de simulação está diferente do esperado"
    fi
    
    if [ "$SIM_LOGS_DIR" != "$GS_LOGS_DIR" ]; then
        echo "⚠️ AVISO: O caminho dos logs no script de simulação está diferente do esperado"
        echo "   Corrigindo o caminho..."
        sed -i "s|GS_LOGS_DIR = \"[^\"]*\"|GS_LOGS_DIR = \"$GS_LOGS_DIR\"|" "$SIM_PATH"
        echo "   ✅ Caminho corrigido"
    fi
else
    echo "❌ ERRO: Script de simulação não encontrado em $SIM_PATH"
fi

# 8. Corrigir todos os scripts Python com caminhos incorretos
echo -e "\n[8/8] Corrigindo caminhos em todos os scripts Python..."
SCRIPTS=$(find /home/istec/projeto_final/satellite -name "*.py")
COUNT=0

for script in $SCRIPTS; do
    if grep -q "/home/istec/projeto_final/GS/logs" "$script" && [ "$script" != "/home/istec/projeto_final/satellite/fix_common_issues.sh" ]; then
        echo "   Corrigindo caminho em $script..."
        sed -i 's|/home/istec/projeto_final/GS/logs|/home/groundstation/projeto_final/GS/logs|g' "$script"
        COUNT=$((COUNT+1))
    fi
done

if [ $COUNT -gt 0 ]; then
    echo "   ✅ Corrigidos $COUNT scripts com caminhos incorretos"
else
    echo "   ✅ Nenhum script com caminho incorreto encontrado"
fi

echo -e "\n=========================================="
echo "RESUMO & PRÓXIMOS PASSOS"
echo "=========================================="
echo "1. Execute o script de inicialização: ./start_satellite.sh"
echo "2. Escolha a opção 7 para verificar a configuração do sistema"
echo "3. Escolha a opção 3 para usar o gerador de telemetria simulada"
echo "4. Acesse o dashboard no navegador: http://${GS_IP}:8000"
echo ""
echo "Se ainda houver problemas, use a opção 5 do menu para diagnósticos mais detalhados."
echo "=========================================="
