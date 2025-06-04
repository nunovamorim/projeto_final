# Resumo do Projeto - Sistema de Simulação de Satélite

## O que foi realizado

1. **Implementação do Sistema Base do Satélite**
   - Criação de quatro tarefas em tempo real com prioridades adequadas
   - Comunicação entre tarefas via filas
   - Sincronização com grupos de eventos
   - Proteção de recursos partilhados com mutexes
   - Monitorização de desempenho e utilização de stack

2. **Comunicação com a Ground Station**
   - Implementação de servidor socket na simulação do satélite
   - Protocolo para troca de comandos e telemetria
   - Interfaces Ground Station em Python: GUI e CLI
   - Configuração de port forwarding no QEMU

3. **Sistema de Build e Execução**
   - Scripts de build para cross-compilação
   - Configuração do QEMU para simulação Cortex-M3
   - Opção de ambiente Docker para isolamento
   - Suporte a networking por socket

4. **Documentação e Organização**
   - Reorganização da documentação na pasta `docs`
   - Criação dos ficheiros `MINIMUM_REQUIREMENTS.md` e `STEP-BY-STEP.md` em português europeu
   - Atualização dos guias de execução e requisitos
   - Instruções detalhadas para utilizadores

## Funcionalidades Principais

- Gestão de tarefas com prioridades e monitorização
- Comunicação robusta por socket
- Simulação de subsistemas: ADCS, consumo de energia, temperatura
- Detecção e tratamento de erros (asserts, falhas de memória, overflow de stack)
- Visualização e monitorização de telemetria
- Interface gráfica interativa para a estação terrestre
- Visualização em tempo real de gráficos de temperatura, voltagem e consumo energético

## Como Executar o Sistema

1. **Simulação do Satélite (Método Recomendado)**
   ```bash
   cd /home/maria.sat/projeto_final/satellite/cortex_qemu_satellite
   python3 satellite_simulator.py
   ```

2. **Ground Station (GUI)**
   ```bash
   cd /home/maria.sat/projeto_final/satellite/cortex_qemu_satellite
   python3 ground_station.py
   ```
   Após iniciar a interface, clique em "Connect" e depois em "Request Telemetry" para visualizar os dados.

3. **Ground Station (CLI)**
   ```bash
   python3 ground_station_cli.py telemetry
   python3 ground_station_cli.py adcs 45.0
   python3 ground_station_cli.py monitor --duration 30
   ```

## Próximos Passos

- Melhorar mecanismos de recuperação de erros
- Simulação de subsistemas adicionais (energia, controlo térmico)
- Interface web para a Ground Station
- Otimização de desempenho
- Finalização e entrega da documentação

## Recomendações de Teste
- Testar comunicação entre satélite e ground station
- Verificar robustez em cenários de falha
- Avaliar desempenho e utilização de recursos
