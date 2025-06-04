#ifndef MAIN_SO_H
#define MAIN_SO_H

#include "FreeRTOS.h"
#include "task.h"
#include "queue.h"
#include "semphr.h"

// Task priorities
#define MAIN_SO_PRIORITY    (configMAX_PRIORITIES - 1)
#define TC_PROC_PRIORITY    (configMAX_PRIORITIES - 2)
#define ADCS_PROC_PRIORITY  (configMAX_PRIORITIES - 3)
#define TM_PROC_PRIORITY    (configMAX_PRIORITIES - 4)

// Queue lengths
#define COMMAND_QUEUE_LENGTH 10
#define TELEMETRY_QUEUE_LENGTH 20

// Command types
typedef enum {
    CMD_ADCS_CONTROL,
    CMD_POWER_CONTROL,
    CMD_TELEMETRY_REQUEST
} CommandType;

// Command structure
typedef struct {
    CommandType type;
    void* parameters;
    size_t param_size;
} Command;

// Task handles
extern TaskHandle_t xMainSOHandle;
extern TaskHandle_t xTCProcHandle;
extern TaskHandle_t xADCSProcHandle;
extern TaskHandle_t xTMProcHandle;

// Queue handles
extern QueueHandle_t xCommandQueue;
extern QueueHandle_t xTelemetryQueue;

// Semaphores
extern SemaphoreHandle_t xResourceMutex;

// Task functions
void vMainSOTask(void *pvParameters);

#endif /* MAIN_SO_H */
