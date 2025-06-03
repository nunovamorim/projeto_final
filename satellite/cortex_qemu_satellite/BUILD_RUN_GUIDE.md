# Satellite Simulation - Build & Run Guide

This guide provides multiple options for building and running the satellite simulation system.

## Option 1: Docker-Based Build and Run

This is the easiest option as it handles all dependencies inside a Docker container.

### Requirements
- Docker installed on your system

### Steps
1. Navigate to the satellite project directory:
   ```bash
   cd /home/maria.sat/projeto_final/satellite/cortex_qemu_satellite
   ```

2. Run the Docker build and run script:
   ```bash
   ./docker_build_run.sh
   ```

3. The script will:
   - Build a Docker image with all required dependencies
   - Run the satellite simulation inside the container
   - Display the output in your terminal

4. To exit the simulation, press `Ctrl+C`

## Option 2: Direct Build and Run on Host System

### Requirements
- ARM GCC toolchain (`arm-none-eabi-gcc`)
- QEMU for ARM emulation (`qemu-system-arm`)
- GNU Make

### Steps
1. Navigate to the project directory:
   ```bash
   cd /home/maria.sat/projeto_final/satellite/cortex_qemu_satellite
   ```

2. Run the build and run script:
   ```bash
   ./build_and_run.sh
   ```

3. To exit QEMU, press `Ctrl+A`, then `X`

## Option 3: Manual Build and Run

For more control over the build process, you can follow these manual steps:

1. Navigate to the GCC build directory:
   ```bash
   cd /home/maria.sat/projeto_final/satellite/cortex_qemu_satellite/build/gcc
   ```

2. Create the output directory:
   ```bash
   mkdir -p output
   ```

3. Build the project (using original Makefile):
   ```bash
   make clean
   make all
   ```

4. Run the simulation with QEMU:
   ```bash
   qemu-system-arm -machine mps2-an385 -cpu cortex-m3 -nographic -semihosting -kernel output/RTOSDemo.out
   ```

## Debugging the Simulation

To debug the satellite simulation, you can use GDB:

1. Start QEMU with GDB server enabled:
   ```bash
   qemu-system-arm -machine mps2-an385 -cpu cortex-m3 -nographic -semihosting -kernel output/RTOSDemo.out -gdb tcp::1234 -S
   ```

2. In another terminal, connect with GDB:
   ```bash
   arm-none-eabi-gdb output/RTOSDemo.out -ex "target remote localhost:1234"
   ```

3. Useful GDB commands:
   - `continue` or `c` - Start/continue execution
   - `break main` - Set breakpoint at main function
   - `info threads` - Show running threads (FreeRTOS tasks)
   - `bt` - Show backtrace

## Monitoring Satellite Telemetry

The simulation outputs telemetry data periodically to the console, including:
- Attitude information (Roll, Pitch, Yaw)
- Temperature
- Power levels
- System status

## System Tasks

The satellite implements four critical tasks:
1. **MAIN_SO**: Central system manager (highest priority)
2. **TC_proc**: Telecommand processor (high priority)
3. **ADCS_proc**: Attitude determination and control (medium priority)
4. **TM_proc**: Telemetry processor (low priority)

## Next Development Steps

1. Implement communication with Ground Station:
   - Socket-based communication between QEMU and external system
   - Dashboard for visualization and control

2. Add robust error handling and recovery:
   - Watchdog timers
   - Comprehensive fault detection

3. Performance testing and optimization:
   - Measure latency in command processing
   - Optimize memory usage
