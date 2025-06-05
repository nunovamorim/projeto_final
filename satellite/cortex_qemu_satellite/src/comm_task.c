#include "FreeRTOS.h"
#include "task.h"
#include "lwip/sockets.h"
#include "protocol.h"
#include <string.h>

#define BUFFER_SIZE 1024
#define GS_PORT 5000
#define RECONNECT_DELAY_MS 5000
#define HEARTBEAT_INTERVAL_MS 1000

static int sock = -1;
static uint8_t rx_buffer[BUFFER_SIZE];
static uint8_t tx_buffer[BUFFER_SIZE];

static bool connect_to_ground_station(const char *gs_ip) {
    struct sockaddr_in server_addr;
    
    // Create socket
    sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock < 0) {
        return false;
    }
    
    // Configure server address
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(GS_PORT);
    if (inet_aton(gs_ip, &server_addr.sin_addr) == 0) {
        close(sock);
        sock = -1;
        return false;
    }
    
    // Connect to ground station
    if (connect(sock, (struct sockaddr*)&server_addr, sizeof(server_addr)) < 0) {
        close(sock);
        sock = -1;
        return false;
    }
    
    return true;
}

static void send_heartbeat(void) {
    int msg_len = create_message(MSG_TYPE_HEARTBEAT, 0, NULL, 0, tx_buffer);
    if (msg_len > 0) {
        send(sock, tx_buffer, msg_len, 0);
    }
}

static void handle_received_message(const uint8_t *buffer, size_t length) {
    int result = process_message(buffer, length);
    
    // If message requires ACK, send it
    const MessageHeader *header = (MessageHeader *)buffer;
    if (header->flags & FLAG_REQUIRES_ACK) {
        int msg_len = create_message(MSG_TYPE_ACK, 0, &header->type, sizeof(uint8_t), tx_buffer);
        if (msg_len > 0) {
            send(sock, tx_buffer, msg_len, 0);
        }
    }
    
    // If there was an error, send error message
    if (result != 0) {
        uint8_t error_code = (uint8_t)result;
        int msg_len = create_message(MSG_TYPE_ERROR, 0, &error_code, sizeof(uint8_t), tx_buffer);
        if (msg_len > 0) {
            send(sock, tx_buffer, msg_len, 0);
        }
    }
}

void comm_task(void *pvParameters) {
    const char *gs_ip = (const char *)pvParameters;
    TickType_t last_heartbeat = xTaskGetTickCount();
    
    while (1) {
        // If not connected, try to connect
        if (sock < 0) {
            if (!connect_to_ground_station(gs_ip)) {
                vTaskDelay(pdMS_TO_TICKS(RECONNECT_DELAY_MS));
                continue;
            }
        }
        
        // Send periodic heartbeat
        TickType_t now = xTaskGetTickCount();
        if ((now - last_heartbeat) >= pdMS_TO_TICKS(HEARTBEAT_INTERVAL_MS)) {
            send_heartbeat();
            last_heartbeat = now;
        }
        
        // Check for incoming messages
        fd_set readfds;
        struct timeval tv = {
            .tv_sec = 0,
            .tv_usec = 100000  // 100ms timeout
        };
        
        FD_ZERO(&readfds);
        FD_SET(sock, &readfds);
        
        int activity = select(sock + 1, &readfds, NULL, NULL, &tv);
        
        if (activity < 0) {
            // Error occurred
            close(sock);
            sock = -1;
            continue;
        }
        
        if (activity > 0 && FD_ISSET(sock, &readfds)) {
            int bytes_received = recv(sock, rx_buffer, BUFFER_SIZE, 0);
            
            if (bytes_received <= 0) {
                // Connection closed or error
                close(sock);
                sock = -1;
                continue;
            }
            
            handle_received_message(rx_buffer, bytes_received);
        }
        
        // Allow other tasks to run
        taskYIELD();
    }
}
