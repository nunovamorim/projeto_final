#!/usr/bin/env python3
"""
Simulador simplificado do servidor de satélite para testes com o ground_station_cli.py e ground_station.py
"""

import socket
import struct
import time
import random
import threading
import math
import sys

# Configurações de comunicação
SERVER_PORT = 10000
BUFFER_SIZE = 1024

# Códigos de comando
CMD_NOP = 0          # No operation
CMD_RESET = 1        # Reset subsystem
CMD_ADCS_SET = 2     # Define ADCS orientation
CMD_GET_TELEMETRY = 3  # Request telemetry
CMD_SET_PARAM = 4    # Set parameter
CMD_SHUTDOWN = 5     # Shutdown subsystem

# Estado do satélite
class SatelliteState:
    def __init__(self):
        self.attitude = [0.0, 0.0, 0.0]  # Roll, Pitch, Yaw
        self.target_attitude = [0.0, 0.0, 0.0]
        self.position = [0.0, 0.0, 0.0]  # X, Y, Z
        self.temperature = 20
        self.power_level = 100
        self.system_status = 1  # 0=erro, 1=nominal, 2=alerta
        self.timestamp = 0

# Instância global do estado do satélite
satellite = SatelliteState()

def calculate_checksum(data):
    """Calculate XOR checksum for the data"""
    checksum = 0
    for b in data:
        checksum ^= b
    return checksum

def update_satellite_state():
    """Update the satellite state periodically"""
    while True:
        # Atualizar timestamp
        satellite.timestamp += 1

        # Simular consumo de energia
        if satellite.power_level > 0:
            satellite.power_level -= 0.1
            if satellite.power_level < 0:
                satellite.power_level = 0

        # Recarga a cada 100 segundos para simular exposição ao sol
        if satellite.timestamp % 100 == 0:
            satellite.power_level = min(100, satellite.power_level + 30)

        # Simular variações na temperatura
        satellite.temperature = 20 + random.uniform(-2, 2)

        # Atualizar atitude - convergência para a atitude alvo
        for i in range(3):
            diff = satellite.target_attitude[i] - satellite.attitude[i]
            if abs(diff) < 0.1:
                satellite.attitude[i] = satellite.target_attitude[i]
            else:
                satellite.attitude[i] += diff * 0.1

            # Normalizar ângulos para 0-360 graus
            while satellite.attitude[i] >= 360.0:
                satellite.attitude[i] -= 360.0
            while satellite.attitude[i] < 0.0:
                satellite.attitude[i] += 360.0

        # Atualizar posição (órbita circular simplificada)
        t = satellite.timestamp / 10.0
        radius = 7000  # km (altitude de órbita LEO)
        satellite.position[0] = radius * math.cos(t * 0.01)
        satellite.position[1] = radius * math.sin(t * 0.01)
        satellite.position[2] = 100 * math.sin(t * 0.05)  # leve variação em z

        # Aguardar próxima atualização
        time.sleep(0.1)

def handle_client(client_socket):
    """Handle client connection"""
    print(f"Ground station connected!")
    
    while True:
        try:
            # Verificar se há dados do cliente
            client_socket.settimeout(0.1)
            try:
                data = client_socket.recv(BUFFER_SIZE)
                if not data:
                    break  # Cliente desconectou
                
                # Processar comando recebido
                if len(data) > 2 and data[0] == 0xAA:
                    cmd_code = data[1]
                    print(f"Comando recebido: {cmd_code}")
                    
                    # Processar comando
                    if cmd_code == CMD_ADCS_SET and len(data) >= 15:
                        # Extrair parâmetro float (ângulo alvo)
                        angle = struct.unpack('f', data[11:15])[0]
                        print(f"Definindo orientação ADCS para {angle} graus")
                        satellite.target_attitude[0] = angle
                        satellite.target_attitude[1] = angle * 0.5
                        satellite.target_attitude[2] = angle * 0.25
                    
                    elif cmd_code == CMD_RESET:
                        # Reset do subsistema
                        if len(data) >= 7:
                            subsystem_id = struct.unpack('I', data[3:7])[0]
                            if subsystem_id == 2:  # ADCS
                                print("Reset do subsistema ADCS")
                                satellite.target_attitude = [0.0, 0.0, 0.0]
                    
                    # Sempre enviar telemetria após receber comando
                    send_telemetry(client_socket)
                
            except socket.timeout:
                # Timeout normal, continue
                pass
            
            # Enviar telemetria periodicamente (a cada 1 segundo)
            if int(time.time()) % 1 == 0:
                send_telemetry(client_socket)
            
            # Pequena pausa para evitar alto uso de CPU
            time.sleep(0.1)
            
        except Exception as e:
            print(f"Erro na comunicação com ground station: {e}")
            break
    
    print("Ground station disconnected")
    client_socket.close()

def send_telemetry(client_socket):
    """Send telemetry packet to the client"""
    try:
        # Follow exact protocol format
        payload = bytearray()
        
        # Add timestamp (uint32)
        payload.extend(struct.pack('<I', satellite.timestamp))
        
        # Add attitude (3 floats)
        for i in range(3):
            payload.extend(struct.pack('<f', float(satellite.attitude[i])))
        
        # Add position (3 floats)
        for i in range(3):
            payload.extend(struct.pack('<f', float(satellite.position[i])))
        
        # Add temperature and power level as uint32 (clamped to valid ranges)
        payload.extend(struct.pack('<I', min(100, int(satellite.temperature))))
        payload.extend(struct.pack('<I', min(100, int(satellite.power_level))))
        
        # Add system status
        payload.append(satellite.system_status)
        
        # Build complete packet
        tlm_packet = bytearray()
        tlm_packet.append(0xBB)  # Header
        tlm_packet.append(0x01)  # Telemetry ID
        tlm_packet.append(len(payload))  # Length
        
        # Add timestamp to header
        tlm_packet.extend(struct.pack('<I', satellite.timestamp))
        
        # Add payload
        tlm_packet.extend(payload)
        
        # Calculate checksum
        checksum = calculate_checksum(tlm_packet)
        tlm_packet.append(checksum)
        
        print(f"Sending telemetry: {len(tlm_packet)} bytes")
        
        # Send telemetry
        client_socket.send(tlm_packet)
        return True
    
    except Exception as e:
        print(f"Error sending telemetry: {e}")
        return False

def main():
    """Main server function"""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        print("Iniciando servidor de simulação do satélite...")
        server_socket.bind(('0.0.0.0', SERVER_PORT))
        server_socket.listen(5)
        
        print(f"Simulador de satélite iniciado na porta {SERVER_PORT}")
        print("Aguardando conexão da estação terrestre...")
        sys.stdout.flush()
        
        # Inicia thread de atualização do estado do satélite
        update_thread = threading.Thread(target=update_satellite_state)
        update_thread.daemon = True
        update_thread.start()
        
        # Loop principal para aceitar conexões
        while True:
            client_sock, addr = server_socket.accept()
            print(f"Conexão aceita de {addr[0]}:{addr[1]}")
            
            # Iniciar thread para lidar com o cliente
            client_thread = threading.Thread(target=handle_client, args=(client_sock,))
            client_thread.daemon = True
            client_thread.start()
            
    except KeyboardInterrupt:
        print("\nDesligando servidor...")
    
    except Exception as e:
        print(f"Erro no servidor: {e}")
    
    finally:
        server_socket.close()

if __name__ == "__main__":
    main()
