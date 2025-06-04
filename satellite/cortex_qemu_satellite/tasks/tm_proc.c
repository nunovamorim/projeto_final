#include <string.h>
#include "tm_proc.h"
#include "tcp_client.h"

// Simulated sensor values
static float temperature = 20.0f;
static float power = 100.0f;
static float battery = 95.0f;

void vTMProcTask(void *pvParameters)
{
    TickType_t xLastWakeTime;
    const TickType_t xFrequency = pdMS_TO_TICKS(1000); // 1 Hz telemetry rate
    TelemetryPacket packet;
    
    // Initialize task timing
    xLastWakeTime = xTaskGetTickCount();
    
    for(;;)
    {
        // Update simulated sensor values with some random variations
        temperature += ((float)rand() / RAND_MAX * 0.2f) - 0.1f; // ±0.1°C variation
        power += ((float)rand() / RAND_MAX * 2.0f) - 1.0f;      // ±1W variation
        battery -= ((float)rand() / RAND_MAX * 0.1f);           // Slow discharge
        
        // Keep values within reasonable ranges
        temperature = fmaxf(15.0f, fminf(25.0f, temperature));
        power = fmaxf(90.0f, fminf(110.0f, power));
        battery = fmaxf(0.0f, fminf(100.0f, battery));
        
        // Prepare telemetry packet
        packet.timestamp = xTaskGetTickCount();
        packet.temperature = temperature;
        packet.power = power;
        packet.battery_level = battery;
        
        // Get ADCS status
        if(xSemaphoreTake(xResourceMutex, portMAX_DELAY) == pdTRUE)
        {
            packet.adcs_status = xGetADCSStatus();
            xSemaphoreGive(xResourceMutex);
        }
        
        // Send telemetry packet
        xSendTelemetry(&packet);
        
        // Wait for next telemetry cycle
        vTaskDelayUntil(&xLastWakeTime, xFrequency);
    }
}

BaseType_t xSendTelemetry(const TelemetryPacket* packet)
{
    if(packet == NULL)
    {
        return pdFAIL;
    }
    
    // Send telemetry packet via TCP
    TCPStatus status = xTCPSend(packet, sizeof(TelemetryPacket));
    
    return (status == TCP_OK) ? pdPASS : pdFAIL;
}
