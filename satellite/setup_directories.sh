#!/bin/bash
# Script para garantir que os diretórios estejam criados e com permissões corretas
# /home/istec/projeto_final/satellite/setup_directories.sh

# IP da Ground Station
GS_IP="192.168.1.96"
GS_USER="groundstation"

# Diretório local de logs temporários
mkdir -p /tmp/sat_logs/{adcs,power,thermal,communication,system}
chmod -R 777 /tmp/sat_logs

# Garantir que os diretórios existam na VMGS
echo "Criando diretórios de logs na VMGS..."
ssh -o StrictHostKeyChecking=no $GS_USER@$GS_IP "mkdir -p /home/$GS_USER/projeto_final/GS/logs/{adcs,power,thermal,communication,system}"
ssh -o StrictHostKeyChecking=no $GS_USER@$GS_IP "chmod -R 777 /home/$GS_USER/projeto_final/GS/logs"

echo "Diretórios criados e permissões configuradas!"
