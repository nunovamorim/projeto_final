#!/bin/bash
set -e  # Exit on error

# Colors for pretty output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Define paths - CORRIGIDO para refletir a estrutura real do projeto
SATELLITE_ROOT="/home/maria.sat/projeto_final/satellite/cortex_qemu_satellite"
FREERTOS_ROOT="/home/maria.sat/projeto_final/satellite/freertos"
BUILD_DIR="${SATELLITE_ROOT}/build/gcc"
OUTPUT_DIR="${BUILD_DIR}/output"

echo -e "${BLUE}====================================================${NC}"
echo -e "${BLUE}   Satellite Simulation System - Corrected Build    ${NC}"
echo -e "${BLUE}====================================================${NC}"

# Step 1: Create output directory
echo -e "${BLUE}[1/5] Creating output directory...${NC}"
mkdir -p ${OUTPUT_DIR}

# Step 2: Copy satellite code to build directory
echo -e "${BLUE}[2/5] Preparing source files...${NC}"
cp ${SATELLITE_ROOT}/main_satellite.c ${BUILD_DIR}/main_satellite.c

# Step 3: Update Makefile.fixed with correct paths
echo -e "${BLUE}[3/5] Updating Makefile paths...${NC}"
sed -i "s|FREERTOS_ROOT = ../../../freertos|FREERTOS_ROOT = ${FREERTOS_ROOT}|g" ${BUILD_DIR}/Makefile.fixed

# Step 4: Build the project with our fixed Makefile
cd ${BUILD_DIR}
echo -e "${BLUE}[4/5] Building the satellite simulation...${NC}"

# Make the binary
make -f Makefile.fixed clean
make -f Makefile.fixed all

if [ $? -ne 0 ]; then
  echo -e "${RED}Build failed!${NC}"
  exit 1
fi

echo -e "${GREEN}Build successful! Binary: ${OUTPUT_DIR}/RTOSDemo.out${NC}"

# Step 5: Run with QEMU
echo -e "${BLUE}[5/5] Running satellite simulation on QEMU...${NC}"
echo -e "${BLUE}Press Ctrl+A, X to exit QEMU${NC}"

qemu-system-arm \
  -machine mps2-an385 \
  -cpu cortex-m3 \
  -nographic \
  -semihosting \
  -netdev user,id=mynet0,hostfwd=tcp::10000-:10000 \
  -device rtl8139,netdev=mynet0 \
  -kernel ${OUTPUT_DIR}/RTOSDemo.out

echo -e "${GREEN}QEMU session ended.${NC}"
