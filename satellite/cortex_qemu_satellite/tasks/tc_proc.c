#include <string.h>
#include "tc_proc.h"
#include "tcp_client.h"

// Buffer for receiving commands
static uint8_t commandBuffer[256];

void vTCProcTask(void *pvParameters)
{
    TCPStatus status;
    Command command;
    size_t received;

    // Initialize TCP connection to Ground Station
    status = xTCPConnect(GS_IP_ADDRESS, GS_PORT);
    if (status != TCP_OK) {
        // Handle connection error
        vTaskDelay(pdMS_TO_TICKS(5000)); // Wait before retry
        return;
    }

    // Task main loop
    for(;;)
    {
        // Wait for incoming command from Ground Station
        status = xTCPReceive(commandBuffer, sizeof(commandBuffer), &received);
        
        if (status == TCP_OK && received > 0)
        {
            // Parse received command
            if (xProcessCommand(&command) == pdPASS)
            {
                // Forward command to MAIN_SO via queue
                if (xQueueSend(xCommandQueue, &command, portMAX_DELAY) != pdPASS)
                {
                    // Handle queue send failure
                    if (command.parameters != NULL)
                    {
                        vPortFree(command.parameters);
                    }
                }
            }
        }
        else if (status == TCP_DISCONNECTED)
        {
            // Handle disconnection and attempt reconnection
            vTCPDisconnect();
            vTaskDelay(pdMS_TO_TICKS(5000));
            status = xTCPConnect(GS_IP_ADDRESS, GS_PORT);
        }

        // Add delay to prevent tight polling
        vTaskDelay(pdMS_TO_TICKS(50));
    }
}

BaseType_t xProcessCommand(const Command* command)
{
    // Parse command from buffer and populate Command structure
    // This is a simplified implementation - in reality, would need proper protocol parsing
    
    Command newCommand;
    uint8_t cmdType = commandBuffer[0]; // First byte indicates command type
    
    switch(cmdType)
    {
        case 0x01: // ADCS Control Command
            newCommand.type = CMD_ADCS_CONTROL;
            newCommand.parameters = pvPortMalloc(sizeof(float) * 3); // For roll, pitch, yaw
            if (newCommand.parameters != NULL)
            {
                memcpy(newCommand.parameters, &commandBuffer[1], sizeof(float) * 3);
                newCommand.param_size = sizeof(float) * 3;
            }
            break;
            
        case 0x02: // Telemetry Request Command
            newCommand.type = CMD_TELEMETRY_REQUEST;
            newCommand.parameters = NULL;
            newCommand.param_size = 0;
            break;
            
        default:
            return pdFAIL;
    }
    
    *command = newCommand;
    return pdPASS;
}
