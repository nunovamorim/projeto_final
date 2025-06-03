#!/usr/bin/env python3
"""
Debug version of Ground Station Client for Satellite Simulation
"""

import socket
import struct
import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
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

class SatelliteData:
    """Class to store and process satellite telemetry data"""
    def __init__(self):
        self.attitude = [0.0, 0.0, 0.0]  # Roll, Pitch, Yaw
        self.position = [0.0, 0.0, 0.0]  # X, Y, Z
        self.temperature = 0
        self.power_level = 0
        self.system_status = 1  # 0=error, 1=nominal, 2=warning
        self.timestamp = 0
        
        # Historical data
        self.history_length = 100
        self.time_history = []
        self.roll_history = []
        self.pitch_history = []
        self.yaw_history = []
        self.temp_history = []
        self.power_history = []
    
    def update(self, data):
        """Update from raw telemetry data"""
        try:
            if len(data) < 37:  # Minimum length check
                print(f"[UPDATE] Data too short: {len(data)} bytes")
                print(f"[UPDATE] Raw data: {' '.join([f'{b:02x}' for b in data])}")
                return False
                
            self.timestamp = struct.unpack('<I', data[0:4])[0]
            self.attitude[0] = struct.unpack('<f', data[4:8])[0]   # Roll
            self.attitude[1] = struct.unpack('<f', data[8:12])[0]  # Pitch
            self.attitude[2] = struct.unpack('<f', data[12:16])[0] # Yaw
            self.position[0] = struct.unpack('<f', data[16:20])[0] # X
            self.position[1] = struct.unpack('<f', data[20:24])[0] # Y
            self.position[2] = struct.unpack('<f', data[24:28])[0] # Z
            self.temperature = struct.unpack('<I', data[28:32])[0]
            self.power_level = struct.unpack('<I', data[32:36])[0]
            self.system_status = data[36]
            
            print(f"[UPDATE] Successfully parsed telemetry:")
            print(f"[UPDATE] Timestamp: {self.timestamp}")
            print(f"[UPDATE] Attitude: Roll={self.attitude[0]:.2f}°, Pitch={self.attitude[1]:.2f}°, Yaw={self.attitude[2]:.2f}°")
            print(f"[UPDATE] Position: X={self.position[0]:.2f}, Y={self.position[1]:.2f}, Z={self.position[2]:.2f}")
            print(f"[UPDATE] Temperature: {self.temperature}°C")
            print(f"[UPDATE] Power Level: {self.power_level}%")
            print(f"[UPDATE] System Status: {self.system_status}")
            
            # Update history
            if len(self.time_history) >= self.history_length:
                self.time_history.pop(0)
                self.roll_history.pop(0)
                self.pitch_history.pop(0)
                self.yaw_history.pop(0)
                self.temp_history.pop(0)
                self.power_history.pop(0)
            
            self.time_history.append(self.timestamp / 10.0)  # Show in seconds
            self.roll_history.append(self.attitude[0])
            self.pitch_history.append(self.attitude[1])
            self.yaw_history.append(self.attitude[2])
            self.temp_history.append(self.temperature)
            self.power_history.append(self.power_level)
            
            return True
            
        except Exception as e:
            print(f"[UPDATE] Error parsing telemetry: {e}")
            print(f"[UPDATE] Data length = {len(data)}")
            if len(data) > 0:
                print(f"[UPDATE] Raw data: {' '.join([f'{b:02x}' for b in data])}")
            return False
    
    def get_status_text(self):
        """Convert status code to text"""
        if self.system_status == 0:
            return "ERROR"
        elif self.system_status == 1:
            return "NOMINAL"
        elif self.system_status == 2:
            return "WARNING"
        else:
            return "UNKNOWN"

class GroundStationGUI:
    """Ground Station Graphical User Interface"""
    def __init__(self, root):
        self.root = root
        self.root.title("Satellite Ground Station")
        self.root.geometry("1200x800")
        
        self.connected = False
        self.socket = None
        self.satellite_data = SatelliteData()
        
        self.create_gui()
        self.update_connection_status()
        
        # Start receiver thread when GUI is ready
        self.root.after(1000, self.start_receiver_thread)
    
    def create_gui(self):
        """Create the GUI components"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Connection frame
        conn_frame = ttk.LabelFrame(main_frame, text="Connection", padding="5")
        conn_frame.pack(fill=tk.X, pady=5)
        
        self.ip_var = tk.StringVar(value=SERVER_IP)
        self.port_var = tk.IntVar(value=SERVER_PORT)
        
        ttk.Label(conn_frame, text="Server IP:").grid(row=0, column=0, padx=5, pady=2)
        ttk.Entry(conn_frame, textvariable=self.ip_var, width=15).grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(conn_frame, text="Port:").grid(row=0, column=2, padx=5, pady=2)
        ttk.Entry(conn_frame, textvariable=self.port_var, width=6).grid(row=0, column=3, padx=5, pady=2)
        
        self.conn_btn = ttk.Button(conn_frame, text="Connect", command=self.toggle_connection)
        self.conn_btn.grid(row=0, column=4, padx=5, pady=2)
        
        self.status_label = ttk.Label(conn_frame, text="Not Connected", foreground="red")
        self.status_label.grid(row=0, column=5, padx=5, pady=2)
        
        # Command frame
        cmd_frame = ttk.LabelFrame(main_frame, text="Command Control", padding="5")
        cmd_frame.pack(fill=tk.X, pady=5)
        
        self.cmd_var = tk.IntVar(value=CMD_NOP)
        self.param1_var = tk.IntVar(value=0)
        self.param2_var = tk.IntVar(value=0)
        self.fparam_var = tk.DoubleVar(value=0.0)
        
        # Command selection
        ttk.Label(cmd_frame, text="Command:").grid(row=0, column=0, padx=5, pady=2, sticky=tk.W)
        cmd_combo = ttk.Combobox(cmd_frame, textvariable=self.cmd_var, width=15)
        cmd_combo['values'] = [(CMD_NOP, "No Operation"), 
                               (CMD_RESET, "Reset"), 
                               (CMD_ADCS_SET, "Set ADCS"), 
                               (CMD_GET_TELEMETRY, "Get Telemetry"),
                               (CMD_SET_PARAM, "Set Parameter"),
                               (CMD_SHUTDOWN, "Shutdown")]
        cmd_combo.grid(row=0, column=1, padx=5, pady=2)
        
        # Parameters
        ttk.Label(cmd_frame, text="Param 1:").grid(row=1, column=0, padx=5, pady=2, sticky=tk.W)
        ttk.Entry(cmd_frame, textvariable=self.param1_var, width=10).grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(cmd_frame, text="Param 2:").grid(row=1, column=2, padx=5, pady=2, sticky=tk.W)
        ttk.Entry(cmd_frame, textvariable=self.param2_var, width=10).grid(row=1, column=3, padx=5, pady=2)
        
        ttk.Label(cmd_frame, text="Float Param:").grid(row=1, column=4, padx=5, pady=2, sticky=tk.W)
        ttk.Entry(cmd_frame, textvariable=self.fparam_var, width=10).grid(row=1, column=5, padx=5, pady=2)
        
        # Send button
        send_btn = ttk.Button(cmd_frame, text="Send Command", command=self.send_command)
        send_btn.grid(row=1, column=6, padx=5, pady=2)
        
        # Telemetry frame
        telemetry_frame = ttk.LabelFrame(main_frame, text="Telemetry Data", padding="5")
        telemetry_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Left side - telemetry values
        left_frame = ttk.Frame(telemetry_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # Telemetry labels
        ttk.Label(left_frame, text="System Status:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.status_value = ttk.Label(left_frame, text="UNKNOWN", foreground="gray")
        self.status_value.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(left_frame, text="Temperature:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.temp_value = ttk.Label(left_frame, text="0°C")
        self.temp_value.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(left_frame, text="Power Level:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.power_value = ttk.Label(left_frame, text="0%")
        self.power_value.grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(left_frame, text="Roll:", font=("Arial", 10, "bold")).grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        self.roll_value = ttk.Label(left_frame, text="0.0°")
        self.roll_value.grid(row=3, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(left_frame, text="Pitch:", font=("Arial", 10, "bold")).grid(row=4, column=0, sticky=tk.W, padx=5, pady=2)
        self.pitch_value = ttk.Label(left_frame, text="0.0°")
        self.pitch_value.grid(row=4, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(left_frame, text="Yaw:", font=("Arial", 10, "bold")).grid(row=5, column=0, sticky=tk.W, padx=5, pady=2)
        self.yaw_value = ttk.Label(left_frame, text="0.0°")
        self.yaw_value.grid(row=5, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Right side - graphs
        right_frame = ttk.Frame(telemetry_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create figures for plots
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(8, 8))
        
        # Attitude plot
        self.ax1.set_title('Satellite Attitude')
        self.ax1.set_ylabel('Degrees')
        self.ax1.grid(True)
        
        # Power & Temperature plot
        self.ax2.set_title('Power & Temperature')
        self.ax2.set_xlabel('Time (s)')
        self.ax2.grid(True)
        
        # Add plots to the GUI
        self.canvas = FigureCanvasTkAgg(self.fig, master=right_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Message frame
        msg_frame = ttk.LabelFrame(main_frame, text="Messages", padding="5")
        msg_frame.pack(fill=tk.X, pady=5)
        
        self.msg_text = tk.Text(msg_frame, height=6, width=80)
        self.msg_text.pack(fill=tk.BOTH, expand=True)
        self.msg_text.config(state=tk.DISABLED)
    
    def start_receiver_thread(self):
        """Start the receiver thread"""
        print("[GUI] Starting receiver thread...")
        if not hasattr(self, 'receiver_thread') or not self.receiver_thread.is_alive():
            self.receiver_thread = threading.Thread(target=self.receive_telemetry, daemon=True)
            self.receiver_thread.start()
            print("[GUI] Receiver thread started")
    
    def toggle_connection(self):
        """Toggle the connection state"""
        if not self.connected:
            self.connect_to_server()
        else:
            self.disconnect_from_server()
    
    def connect_to_server(self):
        """Connect to the satellite server"""
        try:
            server_ip = self.ip_var.get()
            server_port = self.port_var.get()
            
            print(f"[CONNECT] Connecting to {server_ip}:{server_port}...")
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5)
            self.socket.connect((server_ip, server_port))
            
            self.connected = True
            self.update_connection_status()
            self.log_message(f"Connected to {server_ip}:{server_port}")
            print("[CONNECT] Connected successfully")
            
            # Request initial telemetry
            self.cmd_var.set(CMD_GET_TELEMETRY)
            self.send_command()
            
        except Exception as e:
            self.log_message(f"Connection error: {e}")
            print(f"[CONNECT] Connection error: {e}")
            messagebox.showerror("Connection Error", f"Failed to connect: {e}")
    
    def disconnect_from_server(self):
        """Disconnect from the server"""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            finally:
                self.socket = None
                self.connected = False
                self.update_connection_status()
                self.log_message("Disconnected from server")
                print("[CONNECT] Disconnected from server")
    
    def update_connection_status(self):
        """Update the connection status display"""
        if self.connected:
            self.status_label.config(text="Connected", foreground="green")
            self.conn_btn.config(text="Disconnect")
        else:
            self.status_label.config(text="Not Connected", foreground="red")
            self.conn_btn.config(text="Connect")
    
    def calculate_checksum(self, data):
        """Calculate XOR checksum for the data"""
        checksum = 0
        for b in data:
            checksum ^= b
        return checksum
    
    def send_command(self):
        """Send a command to the satellite"""
        if not self.connected:
            messagebox.showwarning("Not Connected", "Please connect to the server first")
            return
        
        try:
            cmd_code = self.cmd_var.get()
            param1 = self.param1_var.get()
            param2 = self.param2_var.get()
            fparam = self.fparam_var.get()
            
            # Prepare command packet
            # Header + CMD_ID + LENGTH + PARAM_1 + PARAM_2 + FPARAM
            header = bytes([0xAA])
            cmd_id = bytes([cmd_code])
            length = bytes([12])  # 4 + 4 + 4 bytes for parameters
            param1_bytes = struct.pack('<I', param1)
            param2_bytes = struct.pack('<I', param2)
            fparam_bytes = struct.pack('<f', fparam)
            
            # Calculate checksum
            data = header + cmd_id + length + param1_bytes + param2_bytes + fparam_bytes
            checksum = self.calculate_checksum(data)
            
            # Send command
            packet = data + bytes([checksum])
            print(f"[SEND] Sending command packet: {' '.join([f'{b:02x}' for b in packet])}")
            self.socket.sendall(packet)
            
            self.log_message(f"Sent command: {cmd_code} with params: {param1}, {param2}, {fparam:.2f}")
            print(f"[SEND] Command sent: {cmd_code} with params: {param1}, {param2}, {fparam:.2f}")
            
        except Exception as e:
            self.log_message(f"Error sending command: {e}")
            print(f"[SEND] Error sending command: {e}")
            messagebox.showerror("Command Error", f"Failed to send command: {e}")
    
    def receive_telemetry(self):
        """Thread function to receive telemetry from the server"""
        while True:
            if self.connected and self.socket:
                try:
                    self.socket.settimeout(0.1)
                    data = self.socket.recv(BUFFER_SIZE)
                    
                    if data and len(data) > 0:
                        print(f"[RECV] Received {len(data)} bytes: {' '.join([f'{b:02x}' for b in data])}")
                        
                        if data[0] == 0xBB:  # Telemetry header
                            print(f"[RECV] Got telemetry header")
                            # Process telemetry packet
                            header_size = 3  # Header (1) + ID (1) + Length (1)
                            timestamp_size = 4  # uint32
                            
                            if len(data) >= header_size:
                                payload_length = data[2]  # Length is at index 2
                                total_expected = header_size + timestamp_size + payload_length + 1  # +1 for checksum
                                
                                print(f"[RECV] Packet info: header={header_size}, timestamp={timestamp_size}, payload={payload_length}, total={total_expected}")
                                
                                if len(data) >= total_expected:
                                    # Extract payload (skip header and timestamp)
                                    payload = data[(header_size + timestamp_size):total_expected-1]  # -1 to exclude checksum
                                print(f"[RECV] Extracted payload: {' '.join([f'{b:02x}' for b in payload])}")
                                
                                # Update satellite data
                                if self.satellite_data.update(payload):
                                    print("[RECV] Successfully updated satellite data")
                                    # Update UI with telemetry
                                    self.root.after(0, self.update_telemetry_display)
                                else:
                                    print("[RECV] Failed to update satellite data")
                                    self.log_message("Failed to parse telemetry data")
                    
                except socket.timeout:
                    # This is expected, just continue
                    pass
                except ConnectionError:
                    print("[RECV] Connection lost")
                    self.log_message("Connection lost")
                    self.root.after(0, self.disconnect_from_server)
                    break
                except Exception as e:
                    self.log_message(f"Error receiving telemetry: {e}")
                    print(f"[RECV] Error receiving telemetry: {e}")
            
            # Sleep a bit to avoid heavy CPU usage
            time.sleep(0.1)
    
    def update_telemetry_display(self):
        """Update the telemetry display with current satellite data"""
        try:
            print("[DISPLAY] Updating telemetry display...")
            
            # Update text values
            self.status_value.config(text=self.satellite_data.get_status_text())
            self.temp_value.config(text=f"{self.satellite_data.temperature}°C")
            self.power_value.config(text=f"{self.satellite_data.power_level}%")
            self.roll_value.config(text=f"{self.satellite_data.attitude[0]:.2f}°")
            self.pitch_value.config(text=f"{self.satellite_data.attitude[1]:.2f}°")
            self.yaw_value.config(text=f"{self.satellite_data.attitude[2]:.2f}°")
            
            # Update color for status
            if self.satellite_data.system_status == 0:
                self.status_value.config(foreground="red")
            elif self.satellite_data.system_status == 1:
                self.status_value.config(foreground="green")
            elif self.satellite_data.system_status == 2:
                self.status_value.config(foreground="orange")
            else:
                self.status_value.config(foreground="gray")
            
            # Update plots if we have data
            if len(self.satellite_data.time_history) > 0:
                # Clear old plots
                self.ax1.clear()
                self.ax2.clear()
                
                # Set titles and labels
                self.ax1.set_title('Satellite Attitude')
                self.ax1.set_ylabel('Degrees')
                self.ax1.grid(True)
                
                self.ax2.set_title('Power & Temperature')
                self.ax2.set_xlabel('Time (s)')
                self.ax2.grid(True)
                
                # Plot attitude data
                self.ax1.plot(self.satellite_data.time_history, self.satellite_data.roll_history, 'r-', label='Roll')
                self.ax1.plot(self.satellite_data.time_history, self.satellite_data.pitch_history, 'g-', label='Pitch')
                self.ax1.plot(self.satellite_data.time_history, self.satellite_data.yaw_history, 'b-', label='Yaw')
                self.ax1.legend()
                
                # Plot power and temperature data
                ax2_power = self.ax2
                ax2_temp = self.ax2.twinx()
                
                power_line = ax2_power.plot(self.satellite_data.time_history, self.satellite_data.power_history, 'g-', label='Power')
                temp_line = ax2_temp.plot(self.satellite_data.time_history, self.satellite_data.temp_history, 'r-', label='Temperature')
                
                ax2_power.set_ylabel('Power Level (%)', color='g')
                ax2_temp.set_ylabel('Temperature (°C)', color='r')
                
                # Add combined legend
                lines = power_line + temp_line
                labels = [l.get_label() for l in lines]
                self.ax2.legend(lines, labels)
                
                # Redraw canvas
                self.canvas.draw()
                print("[DISPLAY] Display updated successfully")
                
        except Exception as e:
            self.log_message(f"Error updating display: {e}")
            print(f"[DISPLAY] Error updating display: {e}")
    
    def log_message(self, message):
        """Add a message to the log"""
        try:
            timestamp = datetime.now().strftime('%H:%M:%S')
            self.msg_text.config(state=tk.NORMAL)
            self.msg_text.insert(tk.END, f"[{timestamp}] {message}\n")
            self.msg_text.see(tk.END)
            self.msg_text.config(state=tk.DISABLED)
            print(f"[LOG] {message}")
        except Exception as e:
            print(f"[LOG] Error logging message: {e}")

def main():
    root = tk.Tk()
    app = GroundStationGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
