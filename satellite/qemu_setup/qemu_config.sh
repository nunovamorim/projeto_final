#!/bin/bash

# Definir variáveis de ambiente
export QEMU_MEMORY=64M  # Limitar memória para simular recursos restritos
export QEMU_CORES=1     # Usar single core
export QEMU_NET="user"  # Configuração de rede básica

# Função para iniciar QEMU com FreeRTOS
start_freertos_qemu() {
    qemu-system-x86_64 \
        -m $QEMU_MEMORY \
        -smp $QEMU_CORES \
        -nographic \
        -kernel ./freertos.bin \
        -net nic,model=virtio \
        -net $QEMU_NET
}