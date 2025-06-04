# Sistema de Simulação de Satélite

Este projeto implementa um sistema de simulação de satélite baseado em FreeRTOS, executado em QEMU para emular um ambiente embebido com recursos limitados.

## Arquitetura do Sistema

O sistema simula quatro tarefas principais:

1. **MAIN_SO**: Gestor central do sistema (prioridade máxima)
2. **TC_proc**: Processador de tele-comandos
3. **ADCS_proc**: Sistema de controlo de atitude
4. **TM_proc**: Processador de telemetria

A comunicação entre tarefas é feita por filas, mutexes e grupos de eventos.

## Requisitos

Consulte o ficheiro `MINIMUM_REQUIREMENTS.md` na pasta `docs` para a lista completa de dependências.

## Como Construir e Executar

### Método Recomendado: Simulador Python

```bash
# Em um terminal, inicie o simulador do satélite
python3 satellite_simulator.py

# Em outro terminal, inicie a estação terrestre
python3 ground_station.py
```

Este método oferece a experiência mais confiável e fácil de usar.

### Métodos Alternativos (Avançados)

#### Script automático (requer ajustes de caminhos)

```bash
./corrected_build_run.sh
```

#### Docker

```bash
sudo docker build -t satellite-simulation .
sudo docker run -it -p 10000:10000 satellite-simulation
```

## Interação com a Ground Station

### Interface Gráfica (Recomendada)
```bash
python3 ground_station.py
```

Com a interface gráfica pode:
- Conectar ao simulador do satélite
- Visualizar telemetria em tempo real
- Ver gráficos de temperatura, voltagem e energia
- Enviar comandos para controle de atitude
- Monitorar o funcionamento do sistema

### Interface de Linha de Comandos
```bash
# Obter telemetria atual
python3 ground_station_cli.py telemetry

# Enviar comando para controlo de atitude
python3 ground_station_cli.py adcs 45.0

# Monitorizar por um período específico
python3 ground_station_cli.py monitor --duration 30
```

## Configuração e Funcionalidades

- Simulação de múltiplos subsistemas (ADCS, Power, Comm)
- Geração de telemetria realista com variações dinâmicas
- Protocolo de comunicação robusto com checksums
- Interface gráfica completa com plots de telemetria
- Estatísticas de desempenho em tempo real
- Simulação de eventos e anomalias do sistema

## Novidades e Melhorias
- Documentação reorganizada na pasta `docs`
- Guias de requisitos e execução em português europeu
- Demonstração funcional do sistema completo com interface gráfica
- Sistema simplificado para execução fácil e confiável
- Documentação de resolução de problemas
