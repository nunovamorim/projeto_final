#ifndef TM_PROC_H
#define TM_PROC_H

#include "FreeRTOS.h"
#include "task.h"
#include "semphr.h"
#include "adcs_proc.h"

// External declarations
extern SemaphoreHandle_t xResourceMutex;

// Telemetry packet structure
typedef struct {
    uint32_t timestamp;
    float temperature;
    float power;
    float battery_level;
    ADCSStatus adcs_status;
} TelemetryPacket;

// Function declarations
void vTMProcTask(void *pvParameters);
BaseType_t xSendTelemetry(const TelemetryPacket* packet);

#endif /* TM_PROC_H */
