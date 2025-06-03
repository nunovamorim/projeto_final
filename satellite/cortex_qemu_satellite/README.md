# Satellite Simulation System

This project implements a satellite simulation system using FreeRTOS running on QEMU emulating a Cortex-M3 processor. The system demonstrates real-time embedded software principles for satellite operation, task prioritization, inter-task communication, and ground station interaction.

## System Architecture

![System Architecture](https://via.placeholder.com/800x400.png?text=Satellite+System+Architecture)

### Core Components

1. **Real-time Operating System**: FreeRTOS provides task scheduling, IPC mechanisms, and resource management
2. **Task Management**: Four critical satellite tasks running with different priorities
3. **Ground Station Communication**: TCP socket-based communication for commanding and telemetry
4. **Resource Monitoring**: Stack usage tracking, task statistics, and error handling

### Primary Tasks

1. **MAIN_SO**: Central system manager (highest priority)
   - Handles system initialization
   - Monitors satellite health and resources
   - Generates periodic statistics

2. **TC_proc**: Telecommand processor (high priority)
   - Processes incoming commands
   - Validates command integrity
   - Routes commands to appropriate subsystems

3. **ADCS_proc**: Attitude Determination and Control System (medium priority)
   - Manages satellite orientation
   - Simulates attitude control dynamics
   - Responds to orientation change commands

4. **TM_proc**: Telemetry processor (low priority)
   - Collects system telemetry
   - Formats and transmits data
   - Responds to telemetry requests

5. **Socket Server**: Ground communication interface
   - Accepts connections from ground station
   - Receives commands and forwards to TC_proc
   - Transmits telemetry to ground station

## Getting Started

### Prerequisites

- ARM GCC Toolchain: `arm-none-eabi-gcc`
- QEMU for ARM emulation: `qemu-system-arm`
- Python 3.6+ (for ground station tools)
- Standard build tools (make, etc.)

### Building and Running

1. **Build and run the satellite simulation**:

   ```bash
   cd /home/maria.sat/projeto_final/satellite/cortex_qemu_satellite
   ./build_and_run.sh
   ```

   This will compile the satellite code and start QEMU with the appropriate settings.

2. **In another terminal, start the ground station interface**:

   ```bash
   # For the GUI interface
   python3 ground_station.py
   
   # OR for the command line interface
   python3 ground_station_cli.py telemetry  # Get current telemetry
   python3 ground_station_cli.py adcs 45.0   # Set ADCS orientation to 45 degrees
   python3 ground_station_cli.py monitor --duration 30  # Monitor telemetry for 30 seconds
   ```

3. **To exit QEMU**, press `Ctrl+A`, then `X`.

## Command Reference

The satellite accepts the following commands:

| Command Code | Name | Description | Parameters |
|--------------|------|-------------|------------|
| 0 | NOP | No operation | None |
| 1 | RESET | Reset subsystem | param1: subsystem ID (2=ADCS) |
| 2 | ADCS_SET | Set orientation | fParam: target angle in degrees |
| 3 | GET_TELEMETRY | Request telemetry | None |
| 4 | SET_PARAM | Set parameter | param1: parameter ID, fParam: value |
| 5 | SHUTDOWN | Shutdown subsystem | param1: subsystem ID |

## Telemetry Data

The telemetry includes:

- **Attitude**: Roll, Pitch, Yaw (degrees)
- **Position**: X, Y, Z (simulated)
- **Temperature**: System temperature (°C)
- **Power Level**: Battery charge (0-100%)
- **System Status**: 0=Error, 1=Nominal, 2=Warning

## Contributing

To enhance this system, consider:

1. Implementing a more sophisticated ADCS model
2. Adding more subsystems (power, thermal, payload)
3. Implementing a full command and data handling system
4. Enhancing the ground station visualization

## Project Status

This project is currently a functional prototype that demonstrates:

- ✅ Core FreeRTOS task management
- ✅ Task prioritization and communication
- ✅ Socket-based ground station interface
- ✅ Simulated satellite subsystems
- ✅ Real-time telemetry
- ✅ Command processing

Next development steps include:
- [ ] Enhanced error handling with watchdog timers
- [ ] More realistic satellite dynamics
- [ ] Additional subsystem simulations
- [ ] Web-based ground station interface

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- FreeRTOS Team for the real-time operating system
- ARM for the Cortex-M architecture
- QEMU Team for the hardware emulation
