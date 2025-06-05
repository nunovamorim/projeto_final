#include <string.h>
#include "FreeRTOS.h"
#include "task.h"
#include "semphr.h"
#include "tcp_client.h"

// Buffer size for TCP communications
#define TCP_BUFFER_SIZE 1024

// Communications buffer
static uint8_t ucTCPBuffer[TCP_BUFFER_SIZE];
static SemaphoreHandle_t xTCPMutex = NULL;

TCPStatus xTCPConnect(const char* ip_address, uint16_t port)
{
    (void)ip_address;
    (void)port;

    if (xTCPMutex == NULL)
    {
        xTCPMutex = xSemaphoreCreateMutex();
        if (xTCPMutex == NULL)
        {
            return TCP_ERROR;
        }
    }
    
    // In a real implementation, this would establish a TCP connection
    // For now, we'll just simulate success
    return TCP_OK;
}

TCPStatus xTCPSend(const void* data, size_t length)
{
    if (data == NULL || length > TCP_BUFFER_SIZE)
    {
        return TCP_ERROR;
    }
    
    if (xSemaphoreTake(xTCPMutex, portMAX_DELAY) == pdTRUE)
    {
        // Copy data to buffer
        memcpy(ucTCPBuffer, data, length);
        
        // Output the data to the QEMU serial port with clear markers
        // Usando um formato mais robusto para evitar problemas de buffer
        printf("\n\n\n\n[SAT_TELEMETRY_BEGIN]\n");
        
        // Primeiro, envie o tamanho para ajudar no parsing
        printf("LENGTH:%zu\n", length);
        
        // Agora, envie os dados em formato hexadecimal com separadores
        for (size_t i = 0; i < length; i++) {
            printf("%02x", ((uint8_t*)data)[i]);
            if ((i + 1) % 16 == 0) printf("\n");
        }
        printf("\n[SAT_TELEMETRY_END]\n\n\n\n");
        
        // Flush stdout para garantir que todos os dados foram enviados
        fflush(stdout);
        
        xSemaphoreGive(xTCPMutex);
        return TCP_OK;
    }
    
    return TCP_ERROR;
}

TCPStatus xTCPReceive(void* buffer, size_t length, size_t* received)
{
    if (buffer == NULL || received == NULL || length > TCP_BUFFER_SIZE)
    {
        return TCP_ERROR;
    }
    
    if (xSemaphoreTake(xTCPMutex, portMAX_DELAY) == pdTRUE)
    {
        // In a real implementation, this would receive data over TCP
        // For now, we'll just simulate receiving some data
        
        // Simulate receiving some data (just for testing)
        const char* test_data = "Test Data";
        size_t test_length = strlen(test_data);
        
        if (length < test_length)
        {
            xSemaphoreGive(xTCPMutex);
            return TCP_ERROR;
        }
        
        memcpy(buffer, test_data, test_length);
        *received = test_length;
        
        xSemaphoreGive(xTCPMutex);
        return TCP_OK;
    }
    
    return TCP_ERROR;
}

void vTCPDisconnect(void)
{
    if (xTCPMutex != NULL)
    {
        vSemaphoreDelete(xTCPMutex);
        xTCPMutex = NULL;
    }
    
    // In a real implementation, this would close the TCP connection
}
