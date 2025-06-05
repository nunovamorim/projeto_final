#!/usr/bin/env python3
# Script para gerar telemetria simulada diretamente para o dashboard
# /home/istec/projeto_final/satellite/generate_telemetry.py

import json
import time
import random
import os
import subprocess
from datetime import datetime
from pathlib import Path

# IP e diretório da Ground Station
GS_IP = "192.168.1.96"
GS_LOGS_DIR = "/home/groundstation/projeto_final/GS/logs"
GS_USER = "groundstation"  # Nome de usuário na VMGS

def generate_timestamp():
    """Gera um timestamp no formato ISO8601"""
    return datetime.now().isoformat()

def write_log_to_gs(category, filename, data):
    """Escreve um arquivo de log na VMGS via SCP, mantendo histórico"""
    log_path = f"{GS_LOGS_DIR}/{category}/{filename}"
    timestamp = generate_timestamp()
    
    # Nova entrada de log
    log_entry = {
        "timestamp": timestamp,
        **data
    }
    
    # Criar diretório localmente primeiro
    local_temp_dir = "/tmp/sat_logs"
    local_category_dir = f"{local_temp_dir}/{category}"
    os.makedirs(local_category_dir, exist_ok=True)
    
    # Nome de arquivo temporário local
    local_file = f"{local_category_dir}/{filename}"
    
    try:
        # Tentar carregar logs existentes
        try:
            # Copiar arquivo da VMGS para local se existir
            subprocess.run([
                "scp", 
                "-o", "StrictHostKeyChecking=no",
                f"{GS_USER}@{GS_IP}:{log_path}", 
                local_file
            ], check=False, capture_output=True)
            
            with open(local_file, 'r') as f:
                log_data = json.load(f)
                
            if not isinstance(log_data, list):
                log_data = [log_data]
        except (FileNotFoundError, json.JSONDecodeError, subprocess.CalledProcessError):
            # Criar novo array se não existir ou não for válido
            log_data = []
            
        # Adicionar nova entrada e limitar a 100 entradas
        log_data.append(log_entry)
        if len(log_data) > 100:
            log_data = log_data[-100:]
            
        # Salvar localmente
        with open(local_file, 'w') as f:
            json.dump(log_data, f, indent=2)
            
        # Copiar para a VMGS
        subprocess.run([
            "scp", 
            "-o", "StrictHostKeyChecking=no",
            local_file, 
            f"{GS_USER}@{GS_IP}:{log_path}"
        ], check=True)
        
        print(f"Log {category}/{filename} enviado com sucesso")
    except Exception as e:
        print(f"Erro ao escrever log {category}/{filename}: {e}")

def main():
    print("Iniciando gerador de telemetria simulada...")
    print(f"Enviando logs para {GS_IP}:{GS_LOGS_DIR}")
    
    # Contador para simular uptime
    uptime = 0
    
    try:
        while True:
            uptime += 1
            timestamp = int(time.time())
            
            # Simulação de temperatura
            temp = 22.5 + (random.random() * 3 - 1.5)  # 21-24°C
            thermal_data = {
                "external": temp + 10.0,  # Simulação de sensor externo
                "internal": temp,
                "battery": temp - 2.0,  # Bateria geralmente mais fria
                "solar_panels": temp + 15.0,  # Painéis solares mais quentes
                "processor": temp + 5.0  # Processador mais quente
            }
            write_log_to_gs("thermal", "temperatures.json", thermal_data)
            
            # Simulação de bateria
            battery_level = 95.0 - (uptime % 1000) / 10.0  # Diminui lentamente, depois volta a 95%
            if battery_level < 85.0:
                battery_level = 95.0
                
            power = 100.0 + (random.random() * 10 - 5)  # 95-105W
            
            battery_data = {
                "level": battery_level,
                "voltage": 3.7 + (battery_level / 100.0) * 0.7,  # 3.7V-4.4V
                "current": 0.1 + (power / 100.0) * 0.5,  # 0.1A-0.6A
                "temperature": temp - 2.0  # Igual ao sensor de bateria
            }
            write_log_to_gs("power", "battery.json", battery_data)
            
            # Simulação de consumo de energia
            consumption_data = {
                "total_watts": power,
                "subsystems": {
                    "comm": power * 0.2,  # 20% do total
                    "adcs": power * 0.3,  # 30% do total
                    "payload": power * 0.3,  # 30% do total
                    "thermal": power * 0.1,  # 10% do total
                    "obc": power * 0.1  # 10% do total
                }
            }
            write_log_to_gs("power", "consumption.json", consumption_data)
            
            # Simulação de atitude (ADCS)
            attitude_data = {
                "roll": (timestamp % 360) * 0.1,  # Varia lentamente
                "pitch": ((timestamp + 120) % 360) * 0.1,  # Defasado
                "yaw": ((timestamp + 240) % 360) * 0.1,  # Defasado
                "stability": 95.0 + (5 * random.random())  # 95-100% estabilidade
            }
            write_log_to_gs("adcs", "attitude.json", attitude_data)
            
            # Simulação de status do sistema
            status_data = {
                "mode": "nominal" if random.random() > 0.05 else "safe",
                "uptime": uptime,
                "memory_usage": 65.0 + (timestamp % 10),  # Varia entre 65-75%
                "cpu_load": 30.0 + (timestamp % 15),  # Varia entre 30-45%
                "orbit_phase_deg": (timestamp / 10.0) % 360.0  # Fase da órbita
            }
            write_log_to_gs("system", "status.json", status_data)
            
            # Simulação de comunicação (rádio)
            radio_data = {
                "signal_strength": 75.0 + (timestamp % 25),  # Varia entre 75-100%
                "bit_error_rate": 0.001 * (1.0 + (timestamp % 5) / 10.0),  # Varia entre 0.001-0.0015
                "packets_sent": int(timestamp / 10),  # Aumenta com o tempo
                "packets_received": int((timestamp / 10) * 0.98),  # 98% dos enviados
                "frequency_drift": (timestamp % 10) / 10000.0 - 0.0005  # ±0.0005 Hz
            }
            write_log_to_gs("communication", "radio.json", radio_data)
            
            # Aguardar antes da próxima atualização (5 segundos)
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\nGerador de telemetria encerrado pelo usuário.")

if __name__ == "__main__":
    main()
