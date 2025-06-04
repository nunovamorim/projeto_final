#ifndef TC_PROC_H
#define TC_PROC_H

#include "FreeRTOS.h"
#include "task.h"
#include "queue.h"
#include "main_so.h"

// TCP connection parameters
#define GS_IP_ADDRESS "192.168.1.96"
#define GS_PORT 5000

// Function declarations
void vTCProcTask(void *pvParameters);
BaseType_t xProcessCommand(const Command* command);

#endif /* TC_PROC_H */
