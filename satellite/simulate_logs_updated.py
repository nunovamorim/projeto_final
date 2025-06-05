#!/usr/bin/env python3
# Satellite log simulator - Executa na VMSat e gera logs na VMGS
# /home/istec/projeto_final/satellite/simulate_logs_updated.py

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
GS_USER = "groundstation"
GS_LOGS_DIR = "/home/groundstation/projeto_final/GS/logs"

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
    
    # Criar diretório local temporário
    os.makedirs(f"/tmp/satgs_logs/{category}", exist_ok=True)
    local_path = f"/tmp/satgs_logs/{category}/{filename}"
    
    # Criar diretório remoto
    remote_dir = f"{GS_LOGS_DIR}/{category}"
    mkdir_cmd = f"ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {GS_USER}@{GS_IP} 'mkdir -p {remote_dir} && chmod 777 {remote_dir}'"
    try:
        subprocess.run(mkdir_cmd, shell=True, check=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    except subprocess.CalledProcessError:
        print(f"Aviso: Não foi possível criar diretório {category} na VMGS")
    
    # Verificar se arquivo remoto existe e recuperá-lo
    check_cmd = f"ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {GS_USER}@{GS_IP} 'if [[ -f {log_path} ]]; then cat {log_path}; else echo \"[]\"; fi'"
    
    try:
        # Obter conteúdo atual do log
        result = subprocess.run(check_cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        current_logs = result.stdout.decode('utf-8').strip()
        
        # Converter para objeto Python
        try:
            logs = json.loads(current_logs)
            if not isinstance(logs, list):
                logs = []
        except json.JSONDecodeError:
            logs = []
        
        # Adicionar nova entrada
        logs.append(log_entry)
        
        # Manter apenas as últimas 100 entradas
        if len(logs) > 100:
            logs = logs[-100:]
        
        # Escrever em arquivo local
        with open(local_path, 'w') as f:
            json.dump(logs, f)
        
        # Transferir para o servidor
        scp_cmd = f"scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {local_path} {GS_USER}@{GS_IP}:{log_path}"
        result = subprocess.run(scp_cmd, shell=True, check=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        
        print(f"✓ Log atualizado: {category}/{filename} ({len(logs)} entradas)")
        return True
    
    except Exception as e:
        print(f"✗ Erro ao atualizar log {category}/{filename}: {e}")
        
        # Tentar criar novo arquivo
        try:
            # Criar novo arquivo com apenas esta entrada
            with open(local_path, 'w') as f:
                json.dump([log_entry], f)
            
            # Transferir para servidor
            scp_cmd = f"scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {local_path} {GS_USER}@{GS_IP}:{log_path}"
            result = subprocess.run(scp_cmd, shell=True, check=True)
            
            print(f"✓ Novo arquivo de log criado: {category}/{filename}")
            return True
        except Exception as e2:
            print(f"✗ Falha definitiva ao criar log {category}/{filename}: {e2}")
            return False

def simulate_satellite_logs():
    """Simula dados de telemetria do satélite"""
    counter = 0
    orbit_phase = 0
    
    print(f"Iniciando simulação de logs do satélite para {GS_IP}...")
    print(f"Os logs serão gravados em: {GS_LOGS_DIR}")
    
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
            
            # Mostrar status a cada 10 iterações
            if counter % 10 == 0:
                print(f"Simulação em execução - {counter} iterações - Fase orbital: {orbit_phase * 180 / math.pi:.1f}°")
            
            # Aguarda para próxima atualização
            time.sleep(5)
            
        except KeyboardInterrupt:
            print("\nSimulação interrompida pelo usuário")
            break
        except Exception as e:
            print(f"Erro na simulação: {e}")
            time.sleep(5)

def check_connection():
    """Verifica a conexão com a VMGS"""
    print(f"Verificando conexão com VMGS ({GS_IP})...")
    
    # Testar ping
    ping_cmd = f"ping -c 1 -W 2 {GS_IP}"
    try:
        result = subprocess.run(ping_cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("✓ VMGS acessível via ping")
    except subprocess.CalledProcessError:
        print("✗ ERRO: VMGS não responde a ping")
        return False
    
    # Testar SSH
    ssh_cmd = f"ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=5 {GS_USER}@{GS_IP} echo 'SSH OK'"
    try:
        result = subprocess.run(ssh_cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("✓ Conexão SSH estabelecida com sucesso")
    except subprocess.CalledProcessError:
        print("✗ ERRO: Não foi possível conectar via SSH")
        print("  Verifique se as credenciais SSH estão corretas")
        return False
    
    # Testar escrita de arquivo
    test_data = {"test": True, "timestamp": generate_timestamp()}
    test_log = "/tmp/ssh_test_log.json"
    
    try:
        with open(test_log, 'w') as f:
            json.dump([test_data], f)
        
        scp_cmd = f"scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {test_log} {GS_USER}@{GS_IP}:/tmp/ssh_test_log.json"
        result = subprocess.run(scp_cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("✓ Teste de escrita de arquivo bem-sucedido")
        return True
    except Exception as e:
        print(f"✗ ERRO no teste de escrita: {e}")
        return False

if __name__ == "__main__":
    print("=================================================")
    print("SIMULADOR DE LOGS DE SATÉLITE (VERSÃO MELHORADA)")
    print("=================================================")
    
    if not check_connection():
        print("\n✗ ERRO: Pré-requisitos não atendidos. Corrigindo...")
        print("Executando script de configuração SSH...")
        try:
            subprocess.run("./setup_ssh_force.sh", shell=True, check=True)
            print("\nTentando novamente a verificação de conexão...")
            if not check_connection():
                print("\n✗ FALHA: Não foi possível estabelecer conexão mesmo após configuração")
                print("Por favor, verifique manualmente a conexão entre as VMs")
                exit(1)
        except Exception as e:
            print(f"✗ Erro ao executar script de configuração: {e}")
            exit(1)
    
    # Iniciar simulação
    simulate_satellite_logs()
