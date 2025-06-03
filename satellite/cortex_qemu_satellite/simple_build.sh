#!/bin/bash

# Set paths
SATELLITE_ROOT="/home/maria.sat/projeto_final/satellite/cortex_qemu_satellite"
BUILD_DIR="${SATELLITE_ROOT}/build/gcc"
OUTPUT_DIR="${BUILD_DIR}/output"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE} Satellite Simulation - Simple Build & Run ${NC}"
echo -e "${BLUE}============================================${NC}"

# Create output directory
echo -e "${BLUE}[1/4] Creating output directory...${NC}"
mkdir -p ${OUTPUT_DIR}

# List of source files
echo -e "${BLUE}[2/4] Preparing to compile source files...${NC}"

# CMSIS include path
CMSIS_PATH="${SATELLITE_ROOT}/CMSIS"

# Compile main_satellite.c
echo -e "${BLUE}[3/4] Compiling satellite source...${NC}"
arm-none-eabi-gcc -c \
  -mcpu=cortex-m3 \
  -mthumb \
  -g3 -O0 \
  -I${CMSIS_PATH} \
  -I${FREERTOS_ROOT}/Source/include \
  -I${FREERTOS_ROOT}/Source/portable/GCC/ARM_CM3 \
  -DDEBUG \
  -o ${OUTPUT_DIR}/main_satellite.o \
  ${SATELLITE_ROOT}/main_satellite.c 2>&1

if [ $? -ne 0 ]; then
  echo -e "${RED}Compilation failed!${NC}"
  exit 1
fi

echo -e "${GREEN}Satellite simulation compiled successfully!${NC}"

# Run the simulation
echo -e "${BLUE}[4/4] Testing with a simple run command...${NC}"
qemu-system-arm --version

echo -e "${GREEN}Build script completed!${NC}"
echo -e "${BLUE}To run a full QEMU simulation with the satellite, you would use:${NC}"
echo -e "qemu-system-arm -machine mps2-an385 -cpu cortex-m3 -nographic -semihosting -kernel output/SatelliteDemo.out"
