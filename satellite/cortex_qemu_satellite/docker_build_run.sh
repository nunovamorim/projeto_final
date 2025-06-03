#!/bin/bash
set -e  # Exit on error

# Colors for pretty output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

DOCKER_IMAGE="satellite-simulation"

echo -e "${BLUE}====================================================${NC}"
echo -e "${BLUE}   Satellite Simulation - Docker Build & Run Script${NC}"
echo -e "${BLUE}====================================================${NC}"

echo -e "${BLUE}[1/3] Building Docker image...${NC}"
docker build -t ${DOCKER_IMAGE} .

if [ $? -ne 0 ]; then
  echo -e "${RED}Docker build failed!${NC}"
  exit 1
fi

echo -e "${GREEN}Docker image built successfully!${NC}"

echo -e "${BLUE}[2/3] Running satellite simulation in Docker...${NC}"
echo -e "${BLUE}Press Ctrl+C to exit the simulation${NC}"

docker run -it --rm ${DOCKER_IMAGE}

echo -e "${GREEN}Docker session ended.${NC}"
