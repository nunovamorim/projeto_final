#!/usr/bin/env python3
"""
Simple command-line tool to interact with the satellite simulation
"""

import socket
import struct
import time
import sys
import argparse
from datetime import datetime

# Communication settings
SERVER_IP = '127.0.0.1'
SERVER_PORT = 10000
BUFFER_SIZE = 1024

# Command codes
CMD_NOP = 0          # No operation
CMD_RESET = 1        # Reset subsystem
CMD_ADCS_SET = 2     # Define ADCS orientation
CMD_GET_TELEMETRY = 3  # Request telemetry
CMD_SET_PARAM = 4    # Set parameter
CMD_SHUTDOWN = 5     # Shutdown subsystem

def calculate_checksum(data):
    """Calculate XOR checksum for the data"""
    checksum = 0
    for b in data:
        checksum ^= b
    return checksum

def format_telemetry(data):
    """Format binary telemetry data into readable text"""
    try:
        # Debug print data length and content
        print(f"DEBUG: Received {len(data)} bytes of telemetry data")
        print(f"DEBUG: Raw data: {' '.join([f'{b:02x}' for b in data])}")
        
        # Parse fields with little-endian format
        timestamp = struct.unpack('<I', data[0:4])[0]
        
        # Extract attitude (3 float values)
        roll = struct.unpack('<f', data[4:8])[0]
        pitch = struct.unpack('<f', data[8:12])[0]
        yaw = struct.unpack('<f', data[12:16])[0]
        
        # Extract position (3 float values)
        pos_x = struct.unpack('<f', data[16:20])[0]
        pos_y = struct.unpack('<f', data[20:24])[0]
        pos_z = struct.unpack('<f', data[24:28])[0]
        
        # Extract other data
        temperature = struct.unpack('<I', data[28:32])[0]
        power_level = struct.unpack('<I', data[32:36])[0]
        system_status = data[36] if len(data) > 36 else 1
        
        # Format the status text
        if system_status == 0:
            status_text = "ERROR"
        elif system_status == 1:
            status_text = "NOMINAL"
        elif system_status == 2:
            status_text = "WARNING"
        else:
            status_text = "UNKNOWN"
        
        # Create formatted output
        output = f"""
=== Satellite Telemetry at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===
Timestamp: {timestamp} ticks
Attitude:
  - Roll:  {roll:.2f}°
  - Pitch: {pitch:.2f}°
  - Yaw:   {yaw:.2f}°
Position (km):
  - X: {pos_x:.2f}
  - Y: {pos_y:.2f}
  - Z: {pos_z:.2f}
Temperature: {temperature}°C
Power Level: {power_level}%
System Status: {status_text}
========================================
"""
        return output
    except Exception as e:
        print(f"Error parsing telemetry: {e}")
        print(f"DEBUG: Data length = {len(data)}")
        if len(data) > 0:
            print(f"DEBUG: First byte = {data[0]:02x}")
        return "Error parsing telemetry data"

def send_command(cmd_code, param1=0, param2=0, fparam=0.0):
    """Send a command to the satellite and return the response"""
    try:
        # Create socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # Connect to server
            print(f"Connecting to {SERVER_IP}:{SERVER_PORT}...")
            sock.connect((SERVER_IP, SERVER_PORT))
            print("Connected successfully")
            
            # Prepare command packet
            # Header + CMD_ID + LENGTH + PARAM_1 + PARAM_2 + FPARAM
            header = bytes([0xAA])
            cmd_id = bytes([cmd_code])
            length = bytes([12])  # 4 + 4 + 4 bytes for parameters
            param1_bytes = struct.pack('I', param1)
            param2_bytes = struct.pack('I', param2)
            fparam_bytes = struct.pack('f', fparam)
            
            # Calculate checksum
            data = header + cmd_id + length + param1_bytes + param2_bytes + fparam_bytes
            checksum = calculate_checksum(data)
            
            # Send command
            sock.sendall(data + bytes([checksum]))
            print(f"Sent command: {cmd_code} with params: {param1}, {param2}, {fparam:.2f}")
            
            # Wait for telemetry response
            print("Waiting for telemetry response...")
            response = b""
            start_time = time.time()
            timeout = 5  # 5 seconds timeout
            
            while time.time() - start_time < timeout:
                try:
                    sock.settimeout(1.0)
                    chunk = sock.recv(BUFFER_SIZE)
                    if chunk:
                        response = chunk
                        if response[0] == 0xBB:  # Telemetry header
                            # Process telemetry packet
                            payload_start = 7  # After header, ID, length, timestamp
                            payload_length = response[2]
                            
                            if len(response) >= payload_start + payload_length:
                                # Extract payload
                                payload = response[payload_start:payload_start+payload_length]
                                print(format_telemetry(payload))
                                return True
                    time.sleep(0.1)
                except socket.timeout:
                    continue
                
            print("No telemetry received in time")
            return False
            
    except ConnectionRefusedError:
        print("Connection refused. Is the satellite simulator running?")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def monitor_telemetry(duration=60):
    """Monitor telemetry for a specified duration (in seconds)"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            print(f"Connecting to {SERVER_IP}:{SERVER_PORT}...")
            sock.connect((SERVER_IP, SERVER_PORT))
            print("Connected successfully. Monitoring telemetry...")
            
            # Send initial telemetry request
            header = bytes([0xAA])
            cmd_id = bytes([CMD_GET_TELEMETRY])
            length = bytes([12])
            params = struct.pack('IIf', 0, 0, 0.0)
            data = header + cmd_id + length + params
            checksum = calculate_checksum(data)
            sock.sendall(data + bytes([checksum]))
            
            start_time = time.time()
            while time.time() - start_time < duration:
                try:
                    sock.settimeout(1.0)
                    data = sock.recv(BUFFER_SIZE)
                    
                    if data and len(data) > 0:
                        if data[0] == 0xBB:  # Telemetry header
                            # Process telemetry packet
                            payload_start = 7  # After header, ID, length, timestamp
                            payload_length = data[2]
                            
                            if len(data) >= payload_start + payload_length:
                                # Extract payload
                                payload = data[payload_start:payload_start+payload_length]
                                print(format_telemetry(payload))
                except socket.timeout:
                    # This is expected, just continue
                    pass
                
                time.sleep(1)  # Poll every second
            
            print("Monitoring completed")
            return True
    
    except ConnectionRefusedError:
        print("Connection refused. Is the satellite simulator running?")
        return False
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Main function to parse arguments and execute commands"""
    parser = argparse.ArgumentParser(description='Satellite Ground Station Command Line Tool')
    
    # Command subparsers
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # NOP command
    nop_parser = subparsers.add_parser('nop', help='No operation command')
    
    # Reset command
    reset_parser = subparsers.add_parser('reset', help='Reset a subsystem')
    reset_parser.add_argument('subsystem', type=int, help='Subsystem ID to reset')
    
    # ADCS command
    adcs_parser = subparsers.add_parser('adcs', help='Set ADCS orientation')
    adcs_parser.add_argument('angle', type=float, help='Target angle in degrees')
    
    # Get telemetry command
    telemetry_parser = subparsers.add_parser('telemetry', help='Request telemetry')
    
    # Monitor telemetry
    monitor_parser = subparsers.add_parser('monitor', help='Monitor telemetry for a period')
    monitor_parser.add_argument('--duration', type=int, default=60, help='Monitoring duration in seconds')
    
    # Set parameter command
    param_parser = subparsers.add_parser('param', help='Set a parameter')
    param_parser.add_argument('param_id', type=int, help='Parameter ID')
    param_parser.add_argument('value', type=float, help='Parameter value')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Execute the appropriate command
    if args.command == 'nop':
        send_command(CMD_NOP)
    elif args.command == 'reset':
        send_command(CMD_RESET, param1=args.subsystem)
    elif args.command == 'adcs':
        send_command(CMD_ADCS_SET, fparam=args.angle)
    elif args.command == 'telemetry':
        send_command(CMD_GET_TELEMETRY)
    elif args.command == 'monitor':
        monitor_telemetry(args.duration)
    elif args.command == 'param':
        send_command(CMD_SET_PARAM, param1=args.param_id, fparam=args.value)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
