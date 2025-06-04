#include <string.h>
#include "main_so.h"
#include "tc_proc.h"
#include "adcs_proc.h"
#include "tm_proc.h"

// Task handles
TaskHandle_t xMainSOHandle = NULL;
TaskHandle_t xTCProcHandle = NULL;
TaskHandle_t xADCSProcHandle = NULL;
TaskHandle_t xTMProcHandle = NULL;

// Queue handles
QueueHandle_t xCommandQueue = NULL;
QueueHandle_t xTelemetryQueue = NULL;

// Semaphores
SemaphoreHandle_t xResourceMutex = NULL;

static void prvSetupHardware(void)
{
    // Initialize QEMU hardware simulation
    // This would include any specific hardware initialization
}

int main(void)
{
    // Initialize hardware
    prvSetupHardware();

    // Create queues
    xCommandQueue = xQueueCreate(COMMAND_QUEUE_LENGTH, sizeof(Command));
    xTelemetryQueue = xQueueCreate(TELEMETRY_QUEUE_LENGTH, sizeof(TelemetryPacket));

    // Create semaphore
    xResourceMutex = xSemaphoreCreateMutex();

    // Create tasks
    xTaskCreate(vMainSOTask, "MAIN_SO", configMINIMAL_STACK_SIZE * 2, NULL,
                MAIN_SO_PRIORITY, &xMainSOHandle);

    xTaskCreate(vTCProcTask, "TC_PROC", configMINIMAL_STACK_SIZE * 2, NULL,
                TC_PROC_PRIORITY, &xTCProcHandle);

    xTaskCreate(vADCSProcTask, "ADCS_PROC", configMINIMAL_STACK_SIZE * 2, NULL,
                ADCS_PROC_PRIORITY, &xADCSProcHandle);

    xTaskCreate(vTMProcTask, "TM_PROC", configMINIMAL_STACK_SIZE * 2, NULL,
                TM_PROC_PRIORITY, &xTMProcHandle);

    // Start the scheduler
    vTaskStartScheduler();

    // Should never reach here
    for(;;);
}
