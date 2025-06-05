#!/bin/bash
# Configurar SSH para comunicação entre VMSat e VMGS
# Este script deve ser executado na VMSat (192.168.1.95)

echo "Configurando conexão SSH da VMSat para VMGS..."

# Gerar chave SSH sem senha
if [ ! -f ~/.ssh/id_rsa ]; then
    echo "Gerando chave SSH sem senha..."
    ssh-keygen -t rsa -N "" -f ~/.ssh/id_rsa
else
    echo "Chave SSH já existe"
fi

# Configurar known_hosts e hosts do SSH
echo "Configurando hosts SSH..."
cat > ~/.ssh/config << EOF
Host vmgs groundstation
    HostName 192.168.1.96
    User groundstation
    IdentityFile ~/.ssh/id_rsa
    StrictHostKeyChecking no
EOF

# Copiar chave pública para o servidor VMGS
echo "Copiando chave para VMGS (192.168.1.96)..."
echo "Você precisará digitar a senha do usuário groundstation na VMGS:"
ssh-copy-id groundstation@192.168.1.96

# Verificar conexão
echo "Testando conexão SSH..."
ssh groundstation@192.168.1.96 echo "Conexão SSH testada com sucesso!"

# Criar a estrutura de diretórios de log na VMGS via SSH
echo "Criando estrutura de logs na VMGS..."
ssh groundstation@192.168.1.96 "mkdir -p /home/groundstation/projeto_final/GS/logs/{adcs,power,thermal,communication,system}"
ssh groundstation@192.168.1.96 "chmod -R 755 /home/groundstation/projeto_final/GS/logs"

echo "Configuração concluída!"
echo "Agora você pode executar: python3 /home/istec/projeto_final/satellite/simulate_logs.py"
