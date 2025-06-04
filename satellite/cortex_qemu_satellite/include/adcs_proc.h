#ifndef ADCS_PROC_H
#define ADCS_PROC_H

#include "FreeRTOS.h"
#include "task.h"
#include "semphr.h"

// External declarations
extern SemaphoreHandle_t xResourceMutex;

// ADCS parameters
typedef struct {
    float roll;
    float pitch;
    float yaw;
    uint8_t mode;  // Current control mode
} ADCSStatus;

// Function declarations
void vADCSProcTask(void *pvParameters);
BaseType_t xUpdateAttitude(const float* angles);
ADCSStatus xGetADCSStatus(void);

#endif /* ADCS_PROC_H */
