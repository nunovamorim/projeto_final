#include <string.h>
#include <math.h>
#include <stdlib.h>
#include "adcs_proc.h"

// Define π if not defined by math.h
#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

// Current ADCS status
static ADCSStatus currentStatus = {0};
static const float MAX_RATE = 0.1f; // Maximum rotation rate (rad/s)

// Mutex for protecting shared resources
extern SemaphoreHandle_t xResourceMutex;

void vADCSProcTask(void *pvParameters)
{
    (void)pvParameters;
    
    TickType_t xLastWakeTime;
    const TickType_t xFrequency = pdMS_TO_TICKS(100); // 10 Hz update rate
    
    // Create mutex if not already created
    if (xResourceMutex == NULL) {
        xResourceMutex = xSemaphoreCreateMutex();
        if (xResourceMutex == NULL) {
            // Failed to create mutex
            return;
        }
    }
    
    // Initialize task timing
    xLastWakeTime = xTaskGetTickCount();
    
    // Initialize ADCS status
    currentStatus.roll = 0.0f;
    currentStatus.pitch = 0.0f;
    currentStatus.yaw = 0.0f;
    currentStatus.mode = 0; // Idle mode
    
    for(;;)
    {
        // Simulate attitude dynamics
        if(xSemaphoreTake(xResourceMutex, portMAX_DELAY) == pdTRUE)
        {
            // Add small random perturbations to simulate environmental effects
            currentStatus.roll += (float)rand() / RAND_MAX * 0.01f - 0.005f;
            currentStatus.pitch += (float)rand() / RAND_MAX * 0.01f - 0.005f;
            currentStatus.yaw += (float)rand() / RAND_MAX * 0.01f - 0.005f;
            
            // Keep angles within [-π, π]
            currentStatus.roll = fmodf(currentStatus.roll + M_PI, 2 * M_PI) - M_PI;
            currentStatus.pitch = fmodf(currentStatus.pitch + M_PI, 2 * M_PI) - M_PI;
            currentStatus.yaw = fmodf(currentStatus.yaw + M_PI, 2 * M_PI) - M_PI;
            
            xSemaphoreGive(xResourceMutex);
        }
        
        // Wait for next control cycle
        vTaskDelayUntil(&xLastWakeTime, xFrequency);
    }
}

BaseType_t xUpdateAttitude(const float* angles)
{
    if(angles == NULL)
    {
        return pdFAIL;
    }
    
    if(xSemaphoreTake(xResourceMutex, portMAX_DELAY) == pdTRUE)
    {
        // Calculate rate-limited command
        float deltaRoll = angles[0] - currentStatus.roll;
        float deltaPitch = angles[1] - currentStatus.pitch;
        float deltaYaw = angles[2] - currentStatus.yaw;
        
        // Apply rate limiting
        deltaRoll = fmaxf(fminf(deltaRoll, MAX_RATE), -MAX_RATE);
        deltaPitch = fmaxf(fminf(deltaPitch, MAX_RATE), -MAX_RATE);
        deltaYaw = fmaxf(fminf(deltaYaw, MAX_RATE), -MAX_RATE);
        
        // Update current attitude
        currentStatus.roll += deltaRoll;
        currentStatus.pitch += deltaPitch;
        currentStatus.yaw += deltaYaw;
        
        // Keep angles within [-π, π]
        currentStatus.roll = fmodf(currentStatus.roll + M_PI, 2 * M_PI) - M_PI;
        currentStatus.pitch = fmodf(currentStatus.pitch + M_PI, 2 * M_PI) - M_PI;
        currentStatus.yaw = fmodf(currentStatus.yaw + M_PI, 2 * M_PI) - M_PI;
        
        xSemaphoreGive(xResourceMutex);
        return pdPASS;
    }
    
    return pdFAIL;
}

ADCSStatus xGetADCSStatus(void)
{
    ADCSStatus status = {0};
    
    if(xSemaphoreTake(xResourceMutex, portMAX_DELAY) == pdTRUE)
    {
        // Make a copy of the current status
        status = currentStatus;
        xSemaphoreGive(xResourceMutex);
    }
    
    return status;
}
