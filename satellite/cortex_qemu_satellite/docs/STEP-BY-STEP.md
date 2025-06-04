# Guia Passo-a-Passo para Execução do Programa

Este guia descreve como executar o software de simulação do satélite e conectar a estação terrestre para visualização de dados.

## Método Recomendado: Simulador Python Nativo

Este método é o mais simples e confiável, utilizando diretamente o simulador Python para o satélite.

1. Certifique-se de que o Python 3 está instalado:
   ```bash
   python3 --version
   ```

2. Abra um terminal e navegue até à directoria do projecto:
   ```bash
   cd /home/maria.sat/projeto_final/satellite/cortex_qemu_satellite
   ```

3. Inicie o simulador do satélite em um terminal:
   ```bash
   python3 satellite_simulator.py
   ```
   
   Deve ver a mensagem:
   ```
   Iniciando servidor de simulação do satélite...
   Simulador de satélite iniciado na porta 10000
   Aguardando conexão da estação terrestre...
   ```

4. Mantenha este terminal aberto e abra outro terminal para executar a interface da estação terrestre.
4. Para sair da simulação, pressione `Ctrl+C`.

## Interface Gráfica da Estação Terrestre

1. Após iniciar o simulador do satélite, abra outro terminal e navegue até à pasta do projeto:
   ```bash
   cd /home/maria.sat/projeto_final/satellite/cortex_qemu_satellite
   ```

2. Verifique se o arquivo `ground_station.py` tem permissão de execução:
   ```bash
   chmod +x ground_station.py
   ```

3. Execute a interface gráfica da estação terrestre:
   ```bash
   python3 ground_station.py
   ```

4. Na interface gráfica:
   - Clique em "Connect" para estabelecer conexão com o simulador
   - Clique em "Request Telemetry" para solicitar telemetria
   - Observe os gráficos em tempo real com os dados do satélite
   - Utilize os controles para enviar comandos ao satélite

## Interface de Linha de Comandos

Se preferir utilizar a linha de comandos em vez da interface gráfica:

1. Com o simulador do satélite em execução, abra outro terminal:
   ```bash
   cd /home/maria.sat/projeto_final/satellite/cortex_qemu_satellite
   ```

2. Execute comandos através do cliente de linha de comandos:
   ```bash
   # Para obter telemetria
   python3 ground_station_cli.py telemetry
   
   # Para enviar um comando de controlo de atitude (45.0 graus)
   python3 ground_station_cli.py adcs 45.0
   
   # Para monitorizar o sistema por 30 segundos
   python3 ground_station_cli.py monitor --duration 30
   ```

## Resolução de Problemas Comuns

1. **Erro ao iniciar a interface gráfica**: Verifique a indentação do arquivo. Se necessário, corrija-o:
   ```bash
   nano ground_station.py
   ```
   (Verifique os blocos try/except para indentação correta)
   
2. **Simulador não inicia**: Verifique se a porta 10000 não está em uso:
   ```bash
   sudo lsof -i :10000
   ```

3. **Erro de conexão**: Certifique-se de que o simulador está em execução e que o IP/porta estão corretos na interface da estação terrestre.

## Métodos Alternativos (Menos Recomendados)

### Opção 1: Utilização de Docker

Este método pode ser útil em alguns ambientes, mas requer mais configuração:

1. Instale e configure o Docker:
   ```bash
   sudo apt update
   sudo apt install -y docker.io
   sudo systemctl start docker
   sudo systemctl enable docker
   sudo usermod -aG docker $USER
   ```

2. Execute o script de construção e execução via Docker (necessita de ajustes):
   ```bash
   cd /home/maria.sat/projeto_final/satellite/cortex_qemu_satellite
   sudo docker build -t satellite-simulation .
   sudo docker run -it -p 10000:10000 --name satellite satellite-simulation
   ```

### Opção 2: Execução via QEMU (Experimental)

Este método requer configuração adicional do FreeRTOS:

1. Instale as dependências necessárias:
   ```bash
   sudo apt update
   sudo apt install -y build-essential git gcc-arm-none-eabi qemu-system-arm
   ```

2. Crie uma versão corrigida do script de execução:
   ```bash
   cp build_and_run.sh corrected_build_run.sh
   chmod +x corrected_build_run.sh
   ```
   
3. Edite o script para usar o caminho correto para o FreeRTOS.

## Considerações Importantes

- O simulador Python (`satellite_simulator.py`) é a forma mais simples e confiável de testar o sistema.
- A interface gráfica da estação terrestre oferece visualização em tempo real dos dados do satélite.
- Mantenha o simulador em execução em um terminal e inicie a estação terrestre em um terminal separado.
- Os caminhos nos scripts podem precisar de ajustes dependendo da sua configuração específica.

> **Nota**: Para testes completos, utilize o simulador Python com a interface gráfica da estação terrestre para visualizar dados em tempo real e enviar comandos facilmente.
