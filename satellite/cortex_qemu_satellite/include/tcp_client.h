#ifndef TCP_CLIENT_H
#define TCP_CLIENT_H

#include "FreeRTOS.h"

// TCP client status
typedef enum {
    TCP_OK,
    TCP_ERROR,
    TCP_DISCONNECTED
} TCPStatus;

// Function declarations
TCPStatus xTCPConnect(const char* ip_address, uint16_t port);
TCPStatus xTCPSend(const void* data, size_t length);
TCPStatus xTCPReceive(void* buffer, size_t length, size_t* received);
void vTCPDisconnect(void);

#endif /* TCP_CLIENT_H */
