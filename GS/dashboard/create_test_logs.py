#!/usr/bin/env python3
# Teste de dashboard - verifica se o dashboard consegue encontrar os logs no caminho certo

import json
import sys
import os
from pathlib import Path

print("Testando configuração do dashboard...")

# Check if logs_path was provided
if len(sys.argv) > 1:
    logs_dir = Path(sys.argv[1])
else:
    logs_dir = Path("/home/istec/projeto_final/GS/logs")

print(f"Verificando diretório de logs: {logs_dir}")

# Check if directory exists
if not logs_dir.exists():
    print(f"ERRO: O diretório {logs_dir} não existe!")
    print("Tentando criar...")
    try:
        os.makedirs(logs_dir, exist_ok=True)
        print(f"Diretório {logs_dir} criado com sucesso.")
    except Exception as e:
        print(f"Erro ao criar diretório: {e}")
        sys.exit(1)

# Create sample logs for testing
print("Criando logs de teste...")

subdirs = ["adcs", "power", "thermal", "communication", "system"]

for subdir in subdirs:
    subdir_path = logs_dir / subdir
    os.makedirs(subdir_path, exist_ok=True)
    print(f"  Criado: {subdir_path}")

# Create sample adcs/attitude.json
attitude_data = [
    {
        "timestamp": "2025-06-05T10:00:00",
        "roll": 1.5,
        "pitch": -2.3,
        "yaw": 0.5,
        "stability": 95.2
    },
    {
        "timestamp": "2025-06-05T10:01:00",
        "roll": 1.8,
        "pitch": -2.1,
        "yaw": 0.7,
        "stability": 94.8
    }
]
with open(logs_dir / "adcs" / "attitude.json", 'w') as f:
    json.dump(attitude_data, f, indent=2)
print("  Criado: adcs/attitude.json")

# Create sample power/battery.json
battery_data = [
    {
        "timestamp": "2025-06-05T10:00:00",
        "level": 85.2,
        "voltage": 3.9,
        "current": 0.15,
        "temperature": 27.5
    },
    {
        "timestamp": "2025-06-05T10:01:00",
        "level": 85.5,
        "voltage": 3.91,
        "current": 0.18,
        "temperature": 27.8
    }
]
with open(logs_dir / "power" / "battery.json", 'w') as f:
    json.dump(battery_data, f, indent=2)
print("  Criado: power/battery.json")

# Create sample thermal/temperatures.json
thermal_data = [
    {
        "timestamp": "2025-06-05T10:00:00",
        "external": 45.2,
        "internal": 24.5,
        "battery": 27.5,
        "solar_panels": 55.8,
        "processor": 38.2
    },
    {
        "timestamp": "2025-06-05T10:01:00",
        "external": 45.5,
        "internal": 24.8,
        "battery": 27.8,
        "solar_panels": 56.2,
        "processor": 38.5
    }
]
with open(logs_dir / "thermal" / "temperatures.json", 'w') as f:
    json.dump(thermal_data, f, indent=2)
print("  Criado: thermal/temperatures.json")

# Create sample communication/radio.json
radio_data = [
    {
        "timestamp": "2025-06-05T10:00:00",
        "signal_strength": 85.2,
        "bit_error_rate": 0.001,
        "packets_sent": 100,
        "packets_received": 98,
        "frequency_drift": -0.0003
    },
    {
        "timestamp": "2025-06-05T10:01:00",
        "signal_strength": 86.5,
        "bit_error_rate": 0.0009,
        "packets_sent": 101,
        "packets_received": 99,
        "frequency_drift": -0.0002
    }
]
with open(logs_dir / "communication" / "radio.json", 'w') as f:
    json.dump(radio_data, f, indent=2)
print("  Criado: communication/radio.json")

# Create sample system/status.json
status_data = [
    {
        "timestamp": "2025-06-05T10:00:00",
        "mode": "nominal",
        "uptime": 3600,
        "memory_usage": 67.5,
        "cpu_load": 35.8,
        "orbit_phase_deg": 120.5
    },
    {
        "timestamp": "2025-06-05T10:01:00",
        "mode": "nominal",
        "uptime": 3660,
        "memory_usage": 68.2,
        "cpu_load": 36.5,
        "orbit_phase_deg": 121.2
    }
]
with open(logs_dir / "system" / "status.json", 'w') as f:
    json.dump(status_data, f, indent=2)
print("  Criado: system/status.json")

# Create sample power/consumption.json
consumption_data = [
    {
        "timestamp": "2025-06-05T10:00:00",
        "total_watts": 3.5,
        "subsystems": {
            "comm": 0.8,
            "adcs": 1.2,
            "payload": 0.9,
            "thermal": 0.3,
            "obc": 0.3
        }
    },
    {
        "timestamp": "2025-06-05T10:01:00",
        "total_watts": 3.6,
        "subsystems": {
            "comm": 0.9,
            "adcs": 1.2,
            "payload": 0.9,
            "thermal": 0.3,
            "obc": 0.3
        }
    }
]
with open(logs_dir / "power" / "consumption.json", 'w') as f:
    json.dump(consumption_data, f, indent=2)
print("  Criado: power/consumption.json")

print("\nLogs de teste criados com sucesso!")
print(f"Agora inicie o dashboard com: cd /home/istec/projeto_final/GS/dashboard && python3 app.py")
print(f"E acesse em seu navegador: http://192.168.1.96:8000")
