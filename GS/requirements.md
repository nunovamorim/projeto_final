# Ground Station (VMGS) Setup Requirements

## System Requirements
- Pop OS! 22.04 LTS
- Python 3.10 or higher
- pip (Python package manager)
- Node.js and npm (for web dashboard)

## Python Packages
```bash
pip install -r requirements.txt
```

Contents of requirements.txt:
- Flask==2.0.1
- Flask-SocketIO==5.1.1
- python-socketio==5.4.0
- python-engineio==4.2.1
- eventlet==0.33.1
- numpy==1.21.2
- pandas==1.3.3
- plotly==5.3.1

## Node.js Packages
```bash
npm install
```

Package.json dependencies:
- socket.io-client
- chart.js
- vue.js
- bootstrap

## Network Configuration
- Fixed IP: 192.168.1.96
- Open ports: 5000 (Flask server), 8080 (Socket.IO)

## Setup Instructions
1. Install system dependencies
2. Clone repository
3. Install Python dependencies
4. Install Node.js dependencies
5. Configure network settings
6. Start the ground station server
