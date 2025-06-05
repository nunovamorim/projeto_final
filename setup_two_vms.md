# Configuração de duas VMs para o Sistema Satélite-Ground Station

## Visão Geral
- **VMSat (192.168.1.95)**: Executa o simulador de satélite e gera os logs
- **VMGS (192.168.1.96)**: Executa a Ground Station e o dashboard

## Preparando a VMSat (192.168.1.95)

1. Configure a comunicação SSH entre as VMs:
```bash
cd /home/istec/projeto_final/satellite
chmod +x setup_ssh.sh
./setup_ssh.sh
```

2. Execute o simulador de logs:
```bash
cd /home/istec/projeto_final/satellite
chmod +x simulate_logs.py
python3 simulate_logs.py
```

## Preparando a VMGS (192.168.1.96)

1. Certifique-se que os diretórios de logs existem:
```bash
mkdir -p /home/groundstation/projeto_final/GS/logs/{adcs,power,thermal,communication,system}
chmod -R 755 /home/groundstation/projeto_final/GS/logs
```

2. Instale as dependências do dashboard:
```bash
cd /home/groundstation/projeto_final/GS/dashboard
pip install flask flask-socketio eventlet
```

3. Inicie o dashboard:
```bash
cd /home/groundstation/projeto_final/GS/dashboard
python3 app.py
```

4. Acesse o dashboard em seu navegador:
```
http://192.168.1.96:8000
```
ou
```
http://localhost:8000
```
(Se você configurou port-forwarding no host)

## Estrutura de Arquivos

### VMSat:
- `/home/istec/projeto_final/satellite/simulate_logs.py`: Script que simula telemetria e envia logs para a VMGS
- `/home/istec/projeto_final/satellite/setup_ssh.sh`: Script para configurar a comunicação SSH

### VMGS:
- `/home/groundstation/projeto_final/GS/logs/`: Diretório onde os logs são armazenados
- `/home/groundstation/projeto_final/GS/dashboard/app.py`: Aplicação web que exibe os dados de telemetria

## Solução de Problemas

1. **Problemas de conexão SSH**
   - Verifique se as duas VMs estão na mesma rede virtual
   - Verifique as configurações de firewall
   - Execute `ping 192.168.1.96` da VMSat para verificar a conectividade

2. **Logs não aparecem**
   - Verifique se o script `simulate_logs.py` está sendo executado sem erros
   - Verifique as permissões do diretório de logs na VMGS
   - Verifique o caminho dos logs no arquivo `app.py`

3. **Dashboard não funciona**
   - Verifique se o Flask está instalado e funcionando 
   - Verifique os logs do Flask para erros
   - Confirme que a porta 8000 está aberta
