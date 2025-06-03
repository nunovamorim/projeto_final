# Satellite Simulation System

This project implements a satellite simulation system using FreeRTOS running on QEMU to emulate a real-time embedded environment with limited resources.

## System Architecture

The satellite simulation consists of four critical tasks:

1. **MAIN_SO**: Central system manager with highest priority
2. **TC_proc**: Telecommand processor with high priority
3. **ADCS_proc**: Attitude determination and control system with medium priority
4. **TM_proc**: Telemetry processor with low priority

The system implements proper inter-task communication via queues, mutexes for shared data protection, and event groups for task synchronization.

## Prerequisites

- **ARM GCC Toolchain**: `arm-none-eabi-gcc` (for cross-compilation)
- **QEMU**: `qemu-system-arm` (for ARM Cortex-M3 simulation)
- **Make**: Build automation tool

## Building and Running

### Option 1: Using the build script

Simply run the included build and run script:

```bash
./build_and_run.sh
```

This script will:
1. Clean the build directory
2. Compile the project
3. Start QEMU with the appropriate settings to run the simulation

### Option 2: Manual build and run

1. Navigate to the build directory:
   ```bash
   cd build/gcc
   ```

2. Create the output directory:
   ```bash
   mkdir -p output
   ```

3. Build the project:
   ```bash
   make clean
   make all
   ```

4. Run the simulation with QEMU:
   ```bash
   qemu-system-arm -machine mps2-an385 -cpu cortex-m3 -nographic -semihosting -kernel output/RTOSDemo.out
   ```

## Exiting QEMU

To exit QEMU, press `Ctrl+A` followed by `X`.

## Project Configuration

- **Clock Speed**: 20MHz (simulating an embedded processor)
- **Heap Size**: 64KB (constrained resources)
- **Minimal Stack Size**: 128 words
- **Run-time Statistics**: Enabled for performance monitoring

## System Features

1. **Task Management**:
   - Priority-based scheduling
   - Stack usage monitoring
   - Performance statistics

2. **Inter-task Communication**:
   - Command queues for telecommand processing
   - Telemetry queues for data distribution
   - Event groups for synchronization

3. **Resource Management**:
   - Mutex for protecting shared satellite data
   - Memory allocation tracking and failure detection
   - Stack overflow detection

4. **Simulation Features**:
   - Attitude control simulation
   - Power consumption modeling
   - Temperature variation
   - Periodic telemetry reporting

## Debugging

The system includes several debugging features:
- Runtime statistics output every 10 seconds
- Stack high water mark reporting
- Error handling with assertion hooks
- Memory allocation failure detection

## Next Steps

- Implement communication with Ground Station
- Add more robust error handling and recovery mechanisms
- Implement watchdog timers
- Add more comprehensive fault detection
- Perform latency testing in command processing
