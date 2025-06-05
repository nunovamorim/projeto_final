#!/usr/bin/env python3
# Satellite log simulator - Executa na VMSat e gera logs na VMGS
# /home/istec/projeto_final/satellite/simulate_logs.py

import json
import time
import random
import os
import socket
import subprocess
from datetime import datetime
from pathlib import Path
import math

# IP e diretório da Ground Station
GS_IP = "192.168.1.96" 
GS_LOGS_DIR = "/home/groundstation/projeto_final/GS/logs"

def generate_timestamp():
    """Gera um timestamp no formato ISO8601"""
    return datetime.now().isoformat()

def write_log_to_gs(category, filename, data):
    """Escreve um arquivo de log na VMGS via SSH, mantendo histórico"""
    log_path = f"{GS_LOGS_DIR}/{category}/{filename}"
    timestamp = generate_timestamp()
    
    # Nova entrada de log
    log_entry = {
        "timestamp": timestamp,
        **data
    }
    
    # Tentar criar diretório antecipadamente (evitar problemas de permissão)
    dir_cmd = f'ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null groundstation@{GS_IP} "mkdir -p {GS_LOGS_DIR}/{category} && chmod 777 {GS_LOGS_DIR}/{category}"'
    try:
        subprocess.run(dir_cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError:
        print(f"Aviso: Não foi possível criar/verificar diretório {category}")
    
    # Carregar logs existentes ou criar novo array
    cmd_read = f'ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null groundstation@{GS_IP} "if [ -f {log_path} ]; then cat {log_path}; else echo \'[]\'; fi"'
    
    try:
        # Ler logs existentes
        result = subprocess.run(cmd_read, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logs_json = result.stdout.decode('utf-8').strip()
        
        try:
            logs = json.loads(logs_json)
            # Se for uma string, converter para lista
            if not isinstance(logs, list):
                logs = []
        except json.JSONDecodeError:
            print(f"Erro ao decodificar JSON de {log_path}, criando nova lista")
            logs = []
        
        # Limitar o tamanho do histórico (últimas 100 leituras)
        MAX_HISTORY = 100
        if len(logs) >= MAX_HISTORY:
            logs = logs[-(MAX_HISTORY-1):]
        
        # Adicionar nova entrada
        logs.append(log_entry)
        
        # Converter para JSON e escapar aspas para shell
        json_data = json.dumps(logs).replace('"', '\\"')
        
        # Escrever logs atualizados - usando arquivo temporário para evitar problemas com caracteres especiais
        tmp_file = f"/tmp/log_{category}_{filename.replace('.', '_')}.json"
        with open(tmp_file, 'w') as f:
            f.write(json.dumps(logs))
        
        # Copiar arquivo para a VMGS
        cmd = f'scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {tmp_file} groundstation@{GS_IP}:{log_path}'
        subprocess.run(cmd, shell=True, check=True)
        print(f"Log atualizado em {category}/{filename} (histórico: {len(logs)} entradas)")
        
    except subprocess.CalledProcessError as e:
        print(f"Erro ao ler/escrever log em {category}/{filename}: {e}")
        # Fallback: Criar novo arquivo
        logs = [log_entry]
        json_data = json.dumps(logs).replace('"', '\\"')
        cmd = f'ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null groundstation@{GS_IP} "mkdir -p {GS_LOGS_DIR}/{category} && echo \'{json_data}\' > {log_path}"'
        subprocess.run(cmd, shell=True, check=True)
        print(f"Novo arquivo de log criado em {category}/{filename}")
    except json.JSONDecodeError:
        print(f"Erro ao decodificar JSON de {category}/{filename}, criando novo arquivo")
        logs = [log_entry]
        json_data = json.dumps(logs).replace('"', '\\"')
        cmd = f'ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null groundstation@{GS_IP} "mkdir -p {GS_LOGS_DIR}/{category} && echo \'{json_data}\' > {log_path}"'
        subprocess.run(cmd, shell=True, check=True)
    
    try:
        subprocess.run(cmd, shell=True, check=True)
        print(f"Log escrito em {category}/{filename}")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao escrever log: {e}")

def simulate_satellite_logs():
    """Simula dados de telemetria do satélite"""
    
    # Counters para simulação de comportamento variável
    counter = 0
    orbit_phase = 0
    
    print("Iniciando simulação de logs do satélite...")
    
    while True:
        try:
            counter += 1
            orbit_phase = (orbit_phase + 0.01) % (2 * math.pi)
            
            # ------- ADCS (Attitude Determination and Control System) -------
            write_log_to_gs("adcs", "attitude.json", {
                "roll": 5 * math.sin(orbit_phase),
                "pitch": 3 * math.cos(orbit_phase * 1.5),
                "yaw": 2 * math.sin(orbit_phase * 0.8),
                "stability": random.uniform(85, 100)
            })
            
            write_log_to_gs("adcs", "magnetometer.json", {
                "x": 50 * math.sin(orbit_phase),
                "y": 45 * math.cos(orbit_phase),
                "z": 30 * math.sin(orbit_phase * 1.2),
                "strength": random.uniform(40, 60)
            })
            
            # ------- Power System -------
            # Simula ciclo de órbita com eclipse
            in_eclipse = math.sin(orbit_phase) < -0.3
            solar_intensity = 0 if in_eclipse else (0.8 + 0.2 * math.sin(orbit_phase)) * 1000
            
            battery_discharge = in_eclipse or random.random() > 0.8  # Às vezes descarrega mesmo com sol
            battery_level = 75 + 20 * math.sin(orbit_phase * 0.2)  # Varia lentamente entre 55% e 95%
            
            write_log_to_gs("power", "battery.json", {
                "level": battery_level,
                "voltage": 3.6 + (battery_level - 50) * 0.01,
                "current": -0.2 if battery_discharge else 0.15,
                "temperature": 25 + 5 * math.sin(orbit_phase)
            })
            
            write_log_to_gs("power", "solar_panels.json", {
                "voltage": 4.2 if in_eclipse else 5.0,
                "current": 0 if in_eclipse else 0.8 + 0.2 * math.sin(orbit_phase),
                "power": solar_intensity,
                "temperature": 10 if in_eclipse else 40 + 10 * math.sin(orbit_phase)
            })
            
            write_log_to_gs("power", "consumption.json", {
                "total_watts": 3.5 + random.uniform(-0.2, 0.3),
                "subsystems": {
                    "comm": 0.8 + random.uniform(-0.1, 0.1),
                    "adcs": 1.2 + random.uniform(-0.1, 0.2),
                    "payload": 0.9 + random.uniform(-0.2, 0.4),
                    "thermal": 0.3 + random.uniform(-0.05, 0.05),
                    "obc": 0.3 + random.uniform(-0.05, 0.05)
                }
            })
            
            # ------- Thermal System -------
            write_log_to_gs("thermal", "temperatures.json", {
                "external": (-20 if in_eclipse else 50) + 10 * math.sin(orbit_phase * 0.5),
                "internal": 22 + 3 * math.sin(orbit_phase * 0.3),
                "battery": 25 + 5 * math.sin(orbit_phase),
                "solar_panels": 10 if in_eclipse else 60 + 15 * math.sin(orbit_phase),
                "processor": 35 + 8 * math.sin(orbit_phase * 0.4) + random.uniform(-1, 1)
            })
            
            # ------- Communication System -------
            # Simula perda de sinal durante parte da órbita
            signal_loss = math.sin(orbit_phase) < -0.5
            signal_strength = 0 if signal_loss else 60 + 30 * math.sin(orbit_phase)
            
            write_log_to_gs("communication", "radio.json", {
                "signal_strength": signal_strength,
                "bit_error_rate": 0.05 if signal_strength < 20 else 0.01 if signal_strength < 40 else 0.001,
                "packets_sent": counter,
                "packets_received": counter if signal_strength > 10 else counter - random.randint(1, 3),
                "frequency_drift": random.uniform(-0.001, 0.001)
            })
            
            # ------- Overall System Status -------
            write_log_to_gs("system", "status.json", {
                "mode": "nominal" if battery_level > 30 and signal_strength > 0 else "low_power",
                "uptime": counter * 5,  # segundos
                "memory_usage": 65 + random.uniform(-5, 5),
                "cpu_load": 35 + 15 * math.sin(orbit_phase * 2) + random.uniform(-5, 5),
                "orbit_phase_deg": orbit_phase * 180 / math.pi
            })
            
            # Aguarda 5 segundos para próxima atualização
            time.sleep(5)
            
        except Exception as e:
            print(f"Erro na simulação: {e}")
            time.sleep(5)

if __name__ == "__main__":
    # Confirmar que temos conexão SSH com a VMGS (desabilitando verificação estrita de chaves)
    try:
        subprocess.run(f"ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=5 groundstation@{GS_IP} echo 'Conexão SSH estabelecida'", 
                      shell=True, check=True, stdout=subprocess.PIPE)
        print(f"Conexão com VMGS ({GS_IP}) verificada com sucesso!")
    except subprocess.CalledProcessError:
        print(f"ERRO: Não foi possível conectar via SSH à VMGS ({GS_IP})")
        print("Por favor, verifique se:")
        print("1. A VMGS está ligada e acessível na rede")
        print("2. As credenciais SSH estão corretas e as chaves foram trocadas")
        print("3. A pasta de logs existe no caminho correto")
        exit(1)
    
    # Iniciar simulação
    simulate_satellite_logs()
