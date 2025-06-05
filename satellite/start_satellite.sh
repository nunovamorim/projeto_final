#!/bin/bash
# /home/istec/projeto_final/satellite/start_satellite.sh
# Script para iniciar o simulador do satélite com diferentes opções

# Diretório base do projeto
BASE_DIR="/home/istec/projeto_final"
SATELLITE_DIR="$BASE_DIR/satellite"
QEMU_DIR="$SATELLITE_DIR/cortex_qemu_satellite"

# Configuração da Ground Station
GS_IP="192.168.1.96"
GS_USER="groundstation"
GS_LOGS_DIR="/home/groundstation/projeto_final/GS/logs"

# Função para verificar se o ambiente está preparado
check_environment() {
    echo "======================================================="
    echo "         VERIFICANDO AMBIENTE DE COMUNICAÇÃO           "
    echo "======================================================="
    
    # Verificar se o diretório /tmp/sat_logs existe
    if [ ! -d "/tmp/sat_logs" ]; then
        echo "[ERRO] Diretório /tmp/sat_logs não encontrado!"
        echo "Criando diretório..."
        mkdir -p /tmp/sat_logs/{adcs,power,thermal,communication,system}
        chmod -R 777 /tmp/sat_logs
    fi
    
    # Verificar conexão SSH com a VMGS
    echo "Verificando conexão SSH com VMGS ($GS_IP)..."
    if ! ping -c 1 $GS_IP &>/dev/null; then
        echo "[ERRO] Não foi possível contactar a VMGS em $GS_IP"
        return 1
    fi
    
    # Verificar se o diretório de logs existe na VMGS
    echo "Verificando diretório de logs na VMGS..."
    if ssh -o StrictHostKeyChecking=no $GS_USER@$GS_IP "[ -d $GS_LOGS_DIR ]" 2>/dev/null; then
        echo "✓ Diretório de logs encontrado na VMGS"
    else
        echo "[AVISO] Diretório de logs não encontrado na VMGS"
        echo "Criando diretórios necessários..."
        /home/istec/projeto_final/satellite/setup_directories.sh
    fi
    
    # Verificar se o módulo random está importado no process_qemu_output.py
    echo "Verificando script de processamento..."
    if ! grep -q "import random" "$SATELLITE_DIR/process_qemu_output.py"; then
        echo "[ERRO] Módulo random não importado em process_qemu_output.py"
        echo "Corrigindo automaticamente..."
        sed -i '1,30s/import os/import os\nimport random/' "$SATELLITE_DIR/process_qemu_output.py"
    else
        echo "✓ Script de processamento verificado"
    fi
    
    echo "Ambiente verificado com sucesso!"
    return 0
}

# Verificar ambiente antes de mostrar o menu
check_environment
if [ $? -ne 0 ]; then
    echo "Há problemas no ambiente que precisam ser resolvidos."
    echo "Execute 'setup_directories.sh' e tente novamente."
    exit 1
fi

# Exibir menu de opções
echo "======================================================"
echo "        SIMULADOR DE SATÉLITE - OPÇÕES INICIAIS       "
echo "======================================================"
echo "1) Iniciar satélite com QEMU (baixa verbosidade)"
echo "2) Iniciar satélite com QEMU (alta verbosidade)"
echo "3) Iniciar apenas gerador de telemetria simulada"
echo "4) Corrigir problemas comuns de comunicação"
echo "5) Diagnosticar problemas de comunicação" 
echo "6) Configurar acesso SSH entre VMs"
echo "7) Verificar configuração do sistema"
echo "8) Sair"
echo "======================================================"
echo -n "Escolha uma opção: "
read opcao

case $opcao in
    1)
        echo "Iniciando satélite com QEMU (baixa verbosidade)..."
        cd $QEMU_DIR
        ./run_qemu.sh
        ;;
    2)
        echo "Iniciando satélite com QEMU (alta verbosidade)..."
        cd $QEMU_DIR
        # Adicionando a flag -d guest_errors,unimp novamente
        qemu-system-arm \
            -M lm3s6965evb \
            -cpu cortex-m3 \
            -nographic \
            -kernel "build/satellite.bin" \
            -serial tcp::5678,server,nowait \
            -d guest_errors,unimp \
            -semihosting \
            -monitor stdio \
            2>&1 | $SATELLITE_DIR/process_qemu_output.py
        ;;
    3)
        echo "Iniciando gerador de telemetria simulada..."
        cd $SATELLITE_DIR
        ./generate_telemetry.py
        ;;
    4)
        echo "Corrigindo problemas comuns de comunicação..."
        cd $SATELLITE_DIR
        chmod +x fix_common_issues.sh
        ./fix_common_issues.sh
        echo "Pressione ENTER para continuar..."
        read
        exec $0  # Reiniciar o script
        ;;
    5)
        echo "Executando diagnóstico de problemas de comunicação..."
        cd $SATELLITE_DIR
        python3 diagnose_logs.py
        echo "Pressione ENTER para continuar..."
        read
        exec $0  # Reiniciar o script
        ;;
    6)
        echo "Configurando acesso SSH entre VMs..."
        cd $SATELLITE_DIR
        chmod +x setup_ssh_force.sh
        ./setup_ssh_force.sh
        echo "Pressione ENTER para continuar..."
        read
        exec $0  # Reiniciar o script
        ;;
    7)
        echo "Verificando configuração do sistema..."
        cd $SATELLITE_DIR
        chmod +x verify_setup.sh
        ./verify_setup.sh
        echo "Pressione ENTER para continuar..."
        read
        exec $0  # Reiniciar o script
        ;;
    8)
        echo "Saindo..."
        exit 0
        ;;
    *)
        echo "Opção inválida!"
        exit 1
        ;;
esac
