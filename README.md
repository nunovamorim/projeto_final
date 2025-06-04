# Satellite Simulation Project

This project implements a satellite simulation system with a FreeRTOS-based satellite controller and a ground station interface. The system consists of two main components running on separate virtual machines:

1. Satellite Simulation (VMSat - 192.168.1.95)
2. Ground Station (VMGS - 192.168.1.96)

## Project Structure

```
.
├── docs/               # Project documentation
├── GS/                # Ground Station implementation
│   ├── dashboard/     # Web-based control interface
│   └── requirements.md
└── satellite/         # Satellite simulation
    └── cortex_qemu_satellite/
```

## Ground Station (VMGS)

The ground station provides a web-based dashboard for monitoring and controlling the satellite. It includes:

- Real-time telemetry visualization
- Command interface for satellite control
- System status monitoring
- TCP/IP communication with the satellite

### Setup Requirements
- Pop OS! 22.04 LTS
- Python 3.10+
- Node.js and npm
- Fixed IP: 192.168.1.96

### Installation
```bash
cd GS
chmod +x setup.sh
./setup.sh
```

## Satellite Simulation (VMSat)

The satellite simulation runs on FreeRTOS using QEMU for hardware emulation. It implements:

- Main System Operating task (MAIN_SO)
- Telecommand Processing (TC_proc)
- Attitude Determination and Control (ADCS_proc)
- Telemetry Processing (TM_proc)

### Setup Requirements
- Ubuntu Server 24.04 LTS
- QEMU
- ARM GCC toolchain
- Fixed IP: 192.168.1.95

### Installation
```bash
cd satellite
chmod +x setup.sh
./setup.sh
```

## Running the System

1. Start the satellite simulation:
```bash
cd satellite/cortex_qemu_satellite/build
qemu-system-arm -M lm3s6965evb -nographic -kernel satellite
```

2. Start the ground station:
```bash
cd GS/dashboard
python3 app.py
```

3. Access the dashboard at http://192.168.1.96:5000

## Project Features

- Real-time satellite control and monitoring
- Simulated ADCS system
- Telemetry collection and visualization
- TCP/IP-based communication
- Web-based ground station interface
- Resource-constrained embedded system simulation

## Documentation

Detailed documentation can be found in the `docs` directory, including:
- System architecture
- Communication protocols
- Setup guides
- API references
