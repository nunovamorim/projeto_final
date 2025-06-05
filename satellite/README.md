# Simulação de Satélite e Telemetria Real

Este diretório contém os scripts e código para executar o simulador de satélite e enviar telemetria real para a Ground Station.

> **Atualização (2025-06-05)**: Corrigida a configuração do usuário na VMGS. Agora todos os scripts usam o usuário correto `groundstation` em vez de `istec`. Veja o arquivo [UPDATES.md](UPDATES.md) para detalhes completos sobre as mudanças.

## Arquivos principais

- `run_qemu.sh` - Script para executar o simulador QEMU do satélite
- `process_qemu_output.py` - Processa a saída do QEMU e extrai a telemetria
- `generate_telemetry.py` - Gera telemetria simulada (alternativa ao QEMU)
- `start_satellite.sh` - Menu para iniciar os diferentes componentes

## Como executar

Para iniciar o sistema completo, execute:

```bash
./start_satellite.sh
```

Este script apresentará um menu com as seguintes opções:
1. Iniciar satélite com QEMU (baixa verbosidade)
2. Iniciar satélite com QEMU (alta verbosidade)
3. Iniciar apenas gerador de telemetria simulada
4. Corrigir problemas comuns de comunicação
5. Diagnosticar problemas de comunicação
6. Sair

## Resolução de problemas

Se o QEMU apresentar muitos erros de "Invalid read", você tem duas opções:
1. Use a opção 1 do menu (baixa verbosidade), que oculta esses erros
2. Use a opção 3 para gerar telemetria simulada sem usar o QEMU

Se houver problemas com a comunicação SSH para a Ground Station, use a opção 4 ou 5 para diagnosticar e corrigir os problemas.

Para verificar se o sistema está configurado corretamente, execute:

```bash
./verify_setup.sh
```

Este script verificará se todos os caminhos de diretórios estão corretos, se a VMGS está acessível e se as permissões estão configuradas corretamente.

## Formato dos dados de telemetria

Os dados de telemetria são enviados em formato JSON para os seguintes arquivos na Ground Station:
- `/GS/logs/thermal/temperatures.json` - Temperaturas do satélite
- `/GS/logs/power/battery.json` - Estado da bateria
- `/GS/logs/power/consumption.json` - Consumo de energia
- `/GS/logs/adcs/attitude.json` - Atitude (orientação) do satélite
- `/GS/logs/system/status.json` - Status do sistema
- `/GS/logs/communication/radio.json` - Status da comunicação
