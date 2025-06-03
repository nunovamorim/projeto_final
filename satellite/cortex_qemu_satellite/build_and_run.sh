#!/bin/bash
set -e  # Exit on error

# Colors for pretty output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Define paths
SATELLITE_ROOT=$(dirname $(readlink -f $0))
FREERTOS_ROOT=${SATELLITE_ROOT}/../../freertos
BUILD_DIR="${SATELLITE_ROOT}/build/gcc"
OUTPUT_DIR="${BUILD_DIR}/output"

echo -e "${BLUE}====================================================${NC}"
echo -e "${BLUE}   Satellite Simulation System - Build & Run Script${NC}"
echo -e "${BLUE}====================================================${NC}"

# Step 1: Create output directory
echo -e "${BLUE}[1/4] Creating output directory...${NC}"
mkdir -p ${OUTPUT_DIR}

# Step 2: Copy our main_satellite.c to the build directory for easier compilation
echo -e "${BLUE}[2/4] Preparing source files...${NC}"
cp ${SATELLITE_ROOT}/main_satellite.c ${BUILD_DIR}/main_satellite.c

# Step 3: Build the project with the original Makefile which has all dependencies set up
cd ${BUILD_DIR}
echo -e "${BLUE}[3/4] Building the satellite simulation...${NC}"

# First modify Makefile to use our satellite code
sed -i 's/SOURCE_FILES += .*main\(_blinky\|_full\|\.c\).*$/SOURCE_FILES += main_satellite.c/g' Makefile

# Make the binary
make clean
make all

if [ $? -ne 0 ]; then
  echo -e "${RED}Build failed!${NC}"
  exit 1
fi

echo -e "${GREEN}Build successful! Binary: ${OUTPUT_DIR}/RTOSDemo.out${NC}"

# Step 4: Run with QEMU
echo -e "${BLUE}[4/4] Running satellite simulation on QEMU...${NC}"
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