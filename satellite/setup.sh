#!/bin/bash

# Update system
echo "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install required packages
echo "Installing development tools and QEMU..."
sudo apt install -y build-essential git cmake gcc-arm-none-eabi qemu-system-arm

# Clone FreeRTOS
echo "Cloning FreeRTOS repository..."
git clone --recurse-submodules https://github.com/FreeRTOS/FreeRTOS.git

# Configure network
echo "Configuring network..."
sudo tee /etc/netplan/01-network-manager-all.yaml << EOF
network:
  version: 2
  renderer: NetworkManager
  ethernets:
    eth0:
      dhcp4: no
      addresses:
        - 192.168.1.95/24
      gateway4: 192.168.1.1
      nameservers:
          addresses: [8.8.8.8, 8.8.4.4]
EOF

# Apply network configuration
sudo netplan apply

# Build satellite software
echo "Building satellite software..."
cd cortex_qemu_satellite
mkdir -p build && cd build
cmake ..
make

echo "Setup complete! You can now run the satellite simulation with:"
echo "qemu-system-arm -M lm3s6965evb -nographic -kernel build/satellite"
