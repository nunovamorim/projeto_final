# Requisitos Mínimos

Para executar o software de simulação do satélite, a máquina deve ter instalados os seguintes pacotes conforme o método escolhido:

## Requisitos Mínimos para o Simulador Python (Recomendado)
- Sistema operativo: Ubuntu 20.04+ ou qualquer distribuição Linux compatível
- Python 3 (versão 3.8 ou superior)
- Bibliotecas Python:
  - socket (padrão)
  - struct (padrão)
  - threading (padrão)
  - time (padrão)
  - random (padrão)
  - matplotlib (para a interface gráfica)
  - tkinter (para a interface gráfica)
  - numpy (para gráficos)

### Instalação dos Requisitos para o Simulador
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-tk
pip3 install matplotlib numpy
```

## Requisitos para Métodos Alternativos

### Opção Docker
- Sistema operativo: Ubuntu 20.04+ ou qualquer distribuição Linux compatível
- Docker Engine (pacote `docker.io`)
- Permissões sudo (ou pertencer ao grupo docker)

### Opção QEMU (Experimental)
- Sistema operativo: Ubuntu 22.04 LTS (ou compatível)
- Ferramentas de desenvolvimento:
  - build-essential
  - git
  - make
- Toolchain ARM:
  - gcc-arm-none-eabi
- Emulador:
  - qemu-system-arm
- Python:
  - python3 (3.8+)
  - python3-pip

## Recomendações

Para executar o sistema completo com a melhor experiência possível, recomendamos:

1. Usar o simulador Python para o satélite (`satellite_simulator.py`)
2. Usar a interface gráfica da estação terrestre para visualizar telemetria e enviar comandos (`ground_station.py`)

Esta combinação oferece uma experiência consistente e confiável sem a complexidade das dependências de baixo nível.

> **Nota**: As opções QEMU/FreeRTOS e Docker são mais complexas e podem requerer configuração adicional dependendo do seu ambiente.
