# Satellite Software Installation Guide

## Prerequisites
- Ubuntu Server 24.04 LTS
- Fixed IP: 192.168.1.95
- QEMU emulator

## Required Packages
```bash
sudo apt update
sudo apt install -y build-essential git cmake gcc-arm-none-eabi qemu-system-arm
```

## FreeRTOS Setup
1. Clone FreeRTOS repository with submodules:
```bash
git clone --recurse-submodules https://github.com/FreeRTOS/FreeRTOS.git
```

2. Build FreeRTOS for CORTEX_LM3S6965_GCC_QEMU:
```bash
cd FreeRTOS
mkdir build && cd build
cmake -DTARGET=CORTEX_LM3S6965_GCC_QEMU ..
make
```

## Network Configuration
- Configure static IP (192.168.1.95)
- Open required ports for communication with Ground Station

## Project Structure
```
satellite/
├── cortex_qemu_satellite/
│   ├── main.c
│   ├── tasks/
│   │   ├── main_so.c
│   │   ├── tc_proc.c
│   │   ├── adcs_proc.c
│   │   └── tm_proc.c
│   ├── include/
│   │   ├── main_so.h
│   │   ├── tc_proc.h
│   │   ├── adcs_proc.h
│   │   └── tm_proc.h
│   └── comm/
│       ├── tcp_client.c
│       └── tcp_client.h
```
