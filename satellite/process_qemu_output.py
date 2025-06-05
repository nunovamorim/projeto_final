#!/usr/bin/env python3
# Script para processar a saída do QEMU e enviar telemetria para a Ground Station
# /home/istec/projeto_final/satellite/process_qemu_output.py

import sys
import re
import json
import time
import binascii
import socket
import subprocess
import struct
import random
from datetime import datetime
from pathlib import Path
import os

# IP e diretório da Ground Station
GS_IP = "192.168.1.96"
GS_LOGS_DIR = "/home/groundstation/projeto_final/GS/logs"
GS_USER = "groundstation"  # Nome de usuário na VMGS

# Formato do pacote de telemetria (conforme struct TelemetryPacket no código C)
# struct TelemetryPacket {
#     uint32_t timestamp;
#     float temperature;
#     float power;
#     float battery_level;
#     uint8_t adcs_status;
# };
TELEMETRY_FORMAT = "<Ifff?xxx"  # Adicionar padding para alinhar em 4 bytes

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

def process_telemetry_data(hex_data):
    """Processa os dados de telemetria do formato binário para JSON"""
    try:
        # Converter hex para binário
        binary_data = binascii.unhexlify(hex_data)
        
        # Desempacotar estrutura
        timestamp, temp, power, battery, adcs_status = struct.unpack(TELEMETRY_FORMAT, binary_data)
        
        # Criar dados de telemetria
        
        # Dados de temperatura
        thermal_data = {
            "external": temp + 10.0,  # Simulação de sensor externo
            "internal": temp,
            "battery": temp - 2.0,  # Bateria geralmente mais fria
            "solar_panels": temp + 15.0,  # Painéis solares mais quentes
            "processor": temp + 5.0  # Processador mais quente
        }
        write_log_to_gs("thermal", "temperatures.json", thermal_data)
        
        # Dados de bateria
        battery_data = {
            "level": battery,
            "voltage": 3.7 + (battery / 100.0) * 0.7,  # 3.7V-4.4V
            "current": 0.1 + (power / 100.0) * 0.5,  # 0.1A-0.6A
            "temperature": temp - 2.0  # Igual ao sensor de bateria
        }
        write_log_to_gs("power", "battery.json", battery_data)
        
        # Dados de consumo de energia
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
        
        # Dados de atitude (ADCS)
        # Gere valores baseados no status do ADCS
        attitude_data = {
            "roll": (timestamp % 360) * 0.1,  # Varia lentamente
            "pitch": ((timestamp + 120) % 360) * 0.1,  # Defasado
            "yaw": ((timestamp + 240) % 360) * 0.1,  # Defasado
            "stability": 95.0 + (5 * (not adcs_status))  # Status afeta estabilidade
        }
        write_log_to_gs("adcs", "attitude.json", attitude_data)
        
        # Dados de status do sistema
        status_data = {
            "mode": "nominal" if adcs_status else "safe",
            "uptime": timestamp,  # Usar timestamp como uptime
            "memory_usage": 65.0 + (timestamp % 10),  # Varia entre 65-75%
            "cpu_load": 30.0 + (timestamp % 15),  # Varia entre 30-45%
            "orbit_phase_deg": (timestamp / 10.0) % 360.0  # Fase da órbita
        }
        write_log_to_gs("system", "status.json", status_data)
        
        # Dados de comunicação (rádio)
        radio_data = {
            "signal_strength": 75.0 + (timestamp % 25),  # Varia entre 75-100%
            "bit_error_rate": 0.001 * (1.0 + (timestamp % 5) / 10.0),  # Varia entre 0.001-0.0015
            "packets_sent": int(timestamp / 10),  # Aumenta com o tempo
            "packets_received": int((timestamp / 10) * 0.98),  # 98% dos enviados
            "frequency_drift": (timestamp % 10) / 10000.0 - 0.0005  # ±0.0005 Hz
        }
        write_log_to_gs("communication", "radio.json", radio_data)
        
        return True
    except Exception as e:
        print(f"Erro ao processar telemetria: {e}")
        return False

def main():
    print("Iniciando processador de saída do QEMU para telemetria real...")
    print(f"Enviando logs para {GS_IP}:{GS_LOGS_DIR}")
    
    # Padrão para detectar telemetria na saída do QEMU
    pattern = re.compile(r'\[SAT_TELEMETRY_BEGIN\](.*?)\[SAT_TELEMETRY_END\]', re.DOTALL)
    
    # Gerar telemetria simulada se não detectarmos a verdadeira
    last_telemetry_time = time.time()
    generate_synthetic_telemetry = True
    
    import os
    # Abrir stdin em modo non-blocking
    import fcntl
    fd = sys.stdin.fileno()
    fl = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
    
    buffer = ""
    
    while True:
        try:
            # Verificar se é necessário gerar telemetria sintética
            current_time = time.time()
            if generate_synthetic_telemetry and (current_time - last_telemetry_time) >= 5:
                print("Gerando telemetria sintética já que não foi detectada telemetria real...")
                
                # Gerar dados sintéticos simples
                timestamp = int(current_time)
                temp = 22.5 + (random.random() * 3 - 1.5)  # 21-24°C
                power = 100.0 + (random.random() * 10 - 5)  # 95-105W
                battery = 95.0 - (timestamp % 100) / 100.0  # Lentamente diminuindo
                adcs_status = True
                
                thermal_data = {
                    "external": temp + 10.0,  # Simulação de sensor externo
                    "internal": temp,
                    "battery": temp - 2.0,  # Bateria geralmente mais fria
                    "solar_panels": temp + 15.0,  # Painéis solares mais quentes
                    "processor": temp + 5.0  # Processador mais quente
                }
                write_log_to_gs("thermal", "temperatures.json", thermal_data)
                
                # Dados de bateria
                battery_data = {
                    "level": battery,
                    "voltage": 3.7 + (battery / 100.0) * 0.7,  # 3.7V-4.4V
                    "current": 0.1 + (power / 100.0) * 0.5,  # 0.1A-0.6A
                    "temperature": temp - 2.0  # Igual ao sensor de bateria
                }
                write_log_to_gs("power", "battery.json", battery_data)
                
                # Dados de consumo de energia
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
                
                last_telemetry_time = current_time
            
            # Tente ler da entrada padrão de forma não bloqueante
            try:
                chunk = sys.stdin.read(4096)
                if not chunk:
                    time.sleep(0.1)  # Evita consumo excessivo de CPU
                    continue
                buffer += chunk
            except (IOError, BlockingIOError):
                # Não há dados disponíveis no momento, então esperamos um pouco
                time.sleep(0.1)
                continue
                
            # Procurar por telemetria no buffer
            match = pattern.search(buffer)
            if match:
                hex_data = match.group(1).strip()
                print(f"Telemetria detectada: {hex_data[:20]}...")
                process_telemetry_data(hex_data)
                generate_synthetic_telemetry = False  # Desabilita telemetria sintética ao detectar real
                last_telemetry_time = time.time()
                # Remove a telemetria processada do buffer
                buffer = buffer[match.end():]
            
            # Se o buffer ficar muito grande, mantemos apenas a parte final
            if len(buffer) > 10000:
                buffer = buffer[-5000:]
                
        except KeyboardInterrupt:
            print("\nProcessador de telemetria encerrado pelo usuário.")
            break
        except Exception as e:
            print(f"Erro no processador de telemetria: {e}")
            time.sleep(1)  # Evita spam de erros

if __name__ == "__main__":
    main()
