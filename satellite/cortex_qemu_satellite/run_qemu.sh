#!/bin/bash

# Configuração da Ground Station
GS_IP="192.168.1.96"
GS_LOGS_DIR="/home/groundstation/projeto_final/GS/logs"

# Diretório onde o binário do satélite está localizado
SATELLITE_DIR="$(pwd)/build"
SATELLITE_BIN="${SATELLITE_DIR}/satellite.bin"

# Verifica se o binário existe
if [ ! -f "$SATELLITE_BIN" ]; then
    echo "Erro: Binário do satélite não encontrado em $SATELLITE_BIN"
    exit 1
fi

# Tornar o script de processamento executável
chmod +x /home/istec/projeto_final/satellite/process_qemu_output.py

echo "Iniciando simulador do satélite com telemetria real..."
echo "Ctrl+C para sair"
echo "Logs serão enviados para VMGS: $GS_IP:$GS_LOGS_DIR"

# Configuração do QEMU usando lm3s6965evb (TI Stellaris)
# Redireciona a saída do QEMU para o script de processamento de telemetria
# Removido o flag '-d guest_errors,unimp' para evitar excesso de logs de erro
qemu-system-arm \
    -M lm3s6965evb \
    -cpu cortex-m3 \
    -nographic \
    -kernel "${SATELLITE_BIN}" \
    -serial tcp::5678,server,nowait \
    -semihosting \
    -monitor stdio \
    2>&1 | /home/istec/projeto_final/satellite/process_qemu_output.py

# Capturar código de saída
exit_code=$?

# Se for interrompido por Ctrl+C, matar todos os processos QEMU
if [ $exit_code -ne 0 ]; then
    echo "Encerrando todos os processos QEMU..."
    pkill -f qemu-system-arm || true
fi
