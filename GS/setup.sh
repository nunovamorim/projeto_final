#!/bin/bash

# Update system
echo "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install system dependencies
echo "Installing system dependencies..."
sudo apt install -y python3 python3-pip nodejs npm

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

# Install Node.js dependencies
echo "Installing Node.js dependencies..."
cd dashboard
npm install

# Configure network
echo "Configuring network..."
# Note: This assumes you're using netplan on Pop!_OS
sudo tee /etc/netplan/01-network-manager-all.yaml << EOF
network:
  version: 2
  renderer: NetworkManager
  ethernets:
    eth0:
      dhcp4: no
      addresses:
        - 192.168.1.96/24
      gateway4: 192.168.1.1
      nameservers:
          addresses: [8.8.8.8, 8.8.4.4]
EOF

# Apply network configuration
sudo netplan apply

# Open required ports in firewall
echo "Configuring firewall..."
sudo ufw allow 5000/tcp
sudo ufw allow 8080/tcp

echo "Setup complete! You can now start the ground station server with:"
echo "cd dashboard && python3 app.py"
