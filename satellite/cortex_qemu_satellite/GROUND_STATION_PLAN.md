# Ground Station Communication Implementation Plan

This document outlines the approach for implementing communication between the satellite simulation and a ground station interface.

## Overview

The ground station interface will allow external systems to:
1. Send telecommands to the satellite
2. Receive telemetry from the satellite
3. Visualize satellite data in real-time
4. Monitor the satellite's status and performance

## Technical Approach

### 1. Socket-Based Communication

We'll implement a socket-based communication channel between QEMU and external systems:

```
+---------------+         +-----------------+         +------------------+
| Satellite Sim |  <--->  | Socket Handler  |  <--->  | Ground Station   |
| (QEMU)        |  TCP/IP | (Socket Server) |  TCP/IP | (Client UI)      |
+---------------+         +-----------------+         +------------------+
```

#### Implementation Steps:

1. **Modify the satellite code to include socket functionality**:
   - Add socket initialization in the main function
   - Create a dedicated communication task for handling socket I/O
   - Implement command reception and validation
   - Set up telemetry transmission

2. **Build a ground station client**:
   - Create a Python-based client application
   - Implement command transmission interface
   - Set up telemetry reception and parsing
   - Build visualization components

### 2. Communication Protocol

We'll design a simple packet-based protocol:

#### Command Packets (Ground → Satellite)
```
+--------+--------+--------+---------+--------+----------+
| HEADER | CMD_ID | LENGTH | PARAM_1 | PARAM_2 | CHECKSUM |
| (0xAA) | (1B)   | (1B)   | (4B)    | (4B)    | (1B)     |
+--------+--------+--------+---------+--------+----------+
```

#### Telemetry Packets (Satellite → Ground)
```
+--------+---------+--------+---------+----------+--------+----------+
| HEADER | TLM_ID  | LENGTH | TIMESTAMP | PAYLOAD  | STATUS | CHECKSUM |
| (0xBB) | (1B)    | (1B)   | (4B)      | (var)    | (1B)   | (1B)     |
+--------+---------+--------+---------+----------+--------+----------+
```

### 3. Socket Server Implementation

```c
// Add to main_satellite.c

#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#define GROUND_PORT 10000
#define MAX_CONNECTIONS 1

// Socket server task
static void prvSocketServerTask(void *pvParameters) {
    int server_fd, client_fd;
    struct sockaddr_in address;
    int opt = 1;
    int addrlen = sizeof(address);
    uint8_t buffer[256];
    
    // Create socket file descriptor
    server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd < 0) {
        printf("Socket server: Error creating socket\n");
        vTaskDelete(NULL);
        return;
    }
    
    // Set socket options
    setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR | SO_REUSEPORT, &opt, sizeof(opt));
    
    // Setup address structure
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(GROUND_PORT);
    
    // Bind socket to port
    if (bind(server_fd, (struct sockaddr *)&address, sizeof(address)) < 0) {
        printf("Socket server: Error binding socket\n");
        close(server_fd);
        vTaskDelete(NULL);
        return;
    }
    
    // Listen for connections
    if (listen(server_fd, MAX_CONNECTIONS) < 0) {
        printf("Socket server: Error listening\n");
        close(server_fd);
        vTaskDelete(NULL);
        return;
    }
    
    printf("Socket server: Started on port %d\n", GROUND_PORT);
    
    while (1) {
        // Accept incoming connection
        client_fd = accept(server_fd, (struct sockaddr *)&address, (socklen_t*)&addrlen);
        if (client_fd < 0) {
            printf("Socket server: Error accepting connection\n");
            vTaskDelay(pdMS_TO_TICKS(1000));
            continue;
        }
        
        printf("Socket server: Ground station connected\n");
        
        // Handle client communication
        while (1) {
            // Receive command
            int bytes_read = recv(client_fd, buffer, sizeof(buffer), 0);
            if (bytes_read <= 0) {
                printf("Socket server: Ground station disconnected\n");
                break;
            }
            
            // Process command
            if (bytes_read > 2 && buffer[0] == 0xAA) {
                Command_t cmd;
                cmd.code = buffer[1];
                cmd.param1 = *((uint32_t*)&buffer[3]);
                cmd.param2 = *((uint32_t*)&buffer[7]);
                cmd.fParam = *((float*)&buffer[11]);
                cmd.checksum = buffer[bytes_read - 1];
                
                // Validate and send to command queue
                if (prvValidateCommand(&cmd)) {
                    if (xQueueSend(xTCQueue, &cmd, pdMS_TO_TICKS(10)) != pdPASS) {
                        printf("Socket server: Command queue full\n");
                    } else {
                        printf("Socket server: Command received and queued\n");
                    }
                } else {
                    printf("Socket server: Invalid command checksum\n");
                }
            }
            
            // Send telemetry if available
            SatelliteData_t tlm;
            if (xQueueReceive(xTMQueue, &tlm, 0) == pdPASS) {
                uint8_t tlm_packet[64];
                tlm_packet[0] = 0xBB;  // Telemetry header
                tlm_packet[1] = 0x01;  // Telemetry ID
                tlm_packet[2] = sizeof(SatelliteData_t) + 7; // Length
                
                // Copy timestamp
                memcpy(&tlm_packet[3], &tlm.timestamp, sizeof(TickType_t));
                
                // Copy payload
                memcpy(&tlm_packet[7], &tlm, sizeof(SatelliteData_t));
                
                // Status byte
                tlm_packet[7 + sizeof(SatelliteData_t)] = tlm.system_status;
                
                // Calculate checksum
                uint8_t checksum = 0;
                for (int i = 0; i < 7 + sizeof(SatelliteData_t); i++) {
                    checksum ^= tlm_packet[i];
                }
                tlm_packet[7 + sizeof(SatelliteData_t) + 1] = checksum;
                
                // Send telemetry
                send(client_fd, tlm_packet, 7 + sizeof(SatelliteData_t) + 2, 0);
            }
            
            vTaskDelay(pdMS_TO_TICKS(50));  // Limit polling rate
        }
        
        close(client_fd);
    }
    
    close(server_fd);
    vTaskDelete(NULL);
}
```

## 4. Ground Station Dashboard

We'll implement a Python-based ground station dashboard using:
- Socket communication for data exchange
- Tkinter or PyQt for the graphical interface
- Matplotlib for data visualization

### Dashboard Features:
1. **Command Interface**:
   - Dropdown for command selection
   - Parameter input fields
   - Send button

2. **Telemetry Display**:
   - Attitude visualization (graphical)
   - Temperature and power level indicators
   - System status display
   - Connection status indicator

3. **Data Logging**:
   - Historical data viewing
   - Data export capabilities

## Implementation Timeline

1. **Week 1**: Socket server implementation in satellite code
2. **Week 2**: Socket client and basic command interface
3. **Week 3**: Telemetry visualization and dashboard implementation
4. **Week 4**: Testing, refinement, and documentation

## Testing Strategy

1. **Unit Testing**:
   - Test command encoding/decoding
   - Test telemetry packet formatting
   - Test checksum validation

2. **Integration Testing**:
   - Test socket connections
   - Test command flows
   - Test telemetry reception

3. **System Testing**:
   - End-to-end testing with QEMU
   - Performance testing
   - Stability testing

## Resources Required

1. Development tools:
   - Python 3.8+
   - PyQt5 or Tkinter
   - Matplotlib
   - Socket libraries

2. Documentation:
   - Protocol specification
   - User interface design
   - Test plans
