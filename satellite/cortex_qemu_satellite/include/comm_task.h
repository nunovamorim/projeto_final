#ifndef COMM_TASK_H
#define COMM_TASK_H

#include "FreeRTOS.h"

// Communication task that handles the satellite-ground station protocol
void comm_task(void *pvParameters);

// Helper functions for other tasks to send messages
BaseType_t send_telemetry_data(const TelemetryData *data);
BaseType_t send_error_message(uint8_t error_code);

#endif // COMM_TASK_H
