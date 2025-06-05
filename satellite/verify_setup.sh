#!/bin/bash
# Script para verificar a configuração do sistema de telemetria
# /home/istec/projeto_final/satellite/verify_setup.sh

echo "===================================================="
echo "       VERIFICANDO CONFIGURAÇÃO DO SISTEMA          "
echo "===================================================="

# Definindo as variáveis
GS_IP="192.168.1.96"
GS_USER="groundstation"
GS_LOGS_DIR="/home/groundstation/projeto_final/GS/logs"

# 1. Verificar todos os arquivos críticos para uso correto do usuário
echo -e "\n[1/5] Verificando configuração de usuário em scripts..."
# Excluir scripts que não precisamos verificar
INCORRECT_FILES=$(find /home/istec/projeto_final/satellite -type f -name "*.py" -o -name "*.sh" | grep -v "verify_setup.sh" | grep -v "fix_common_issues.sh" | xargs grep -l "/home/istec/projeto_final/GS/logs" 2>/dev/null || true)

if [ -n "$INCORRECT_FILES" ]; then
  echo "❌ ATENÇÃO: Ainda existem arquivos com caminho incorreto:"
  echo "$INCORRECT_FILES"
  echo "   Execute o script start_satellite.sh e escolha a opção 4 para corrigir automaticamente."
else
  echo "✅ Todos os arquivos parecem usar o caminho correto para logs da GS!"
fi

# 2. Verificar ping para VMGS
echo -e "\n[2/5] Verificando conexão com VMGS (${GS_IP})..."
if ping -c 2 ${GS_IP} > /dev/null; then
    echo "✅ VMGS acessível via ping"
else
    echo "❌ ERRO: Não foi possível conectar à VMGS via ping"
    echo "   Verifique se a VM está ligada e se o IP está correto"
fi

# 3. Verificar SSH com a VMGS
echo -e "\n[3/5] Verificando conexão SSH com VMGS..."
if ssh -o ConnectTimeout=3 -o StrictHostKeyChecking=no -o PasswordAuthentication=no ${GS_USER}@${GS_IP} "echo 'SSH OK'" &>/dev/null; then
    echo "✅ Conexão SSH estabelecida com sucesso"
else
    echo "❌ ERRO: Não foi possível conectar via SSH"
    echo "   Execute o script setup_ssh_force.sh para configurar as chaves SSH"
fi

# 4. Verificar estrutura de diretórios na VMGS
echo -e "\n[4/5] Verificando estrutura de diretórios na VMGS..."
if ssh -o ConnectTimeout=3 -o StrictHostKeyChecking=no ${GS_USER}@${GS_IP} "[ -d ${GS_LOGS_DIR} ]" 2>/dev/null; then
    echo "✅ Diretório principal de logs existe"
    
    # Verificar subdiretorios
    for subdir in "adcs" "power" "thermal" "communication" "system"; do
        if ssh -o ConnectTimeout=3 -o StrictHostKeyChecking=no ${GS_USER}@${GS_IP} "[ -d ${GS_LOGS_DIR}/${subdir} ]" 2>/dev/null; then
            echo "  ✅ Subdiretório ${subdir} existe"
        else
            echo "  ❌ Subdiretório ${subdir} não existe"
            MISSING_DIRS=1
        fi
    done
    
    if [ "$MISSING_DIRS" == "1" ]; then
        echo "   Execute o script setup_directories.sh para criar os diretórios faltantes"
    fi
else
    echo "❌ Diretório de logs não existe na VMGS"
    echo "   Execute o script setup_directories.sh para criar a estrutura necessária"
fi

# 5. Testar escrita de arquivo
echo -e "\n[5/5] Testando escrita de arquivo na VMGS..."
TEST_CONTENT="{\"test\":\"ok\",\"timestamp\":\"$(date -Iseconds)\"}"
TEST_FILE="${GS_LOGS_DIR}/system/test_verify.json"

if ssh -o ConnectTimeout=3 -o StrictHostKeyChecking=no ${GS_USER}@${GS_IP} "echo '[${TEST_CONTENT}]' > ${TEST_FILE}" 2>/dev/null; then
    echo "✅ Arquivo de teste escrito com sucesso"
    
    # Verificar conteúdo
    CONTENT=$(ssh -o ConnectTimeout=3 -o StrictHostKeyChecking=no ${GS_USER}@${GS_IP} "cat ${TEST_FILE}" 2>/dev/null)
    if [ -n "$CONTENT" ]; then
        echo "   Conteúdo do arquivo: $CONTENT"
    fi
else
    echo "❌ Não foi possível escrever arquivo de teste"
    echo "   Verifique as permissões dos diretórios"
fi

echo -e "\n===================================================="
echo "             VERIFICAÇÃO CONCLUÍDA                    "
echo "===================================================="
echo "Se todos os testes passaram, o sistema está pronto para uso!"
echo "Execute ./start_satellite.sh para iniciar o simulador"
echo "===================================================="
