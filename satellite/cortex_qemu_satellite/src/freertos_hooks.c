#include "FreeRTOS.h"
#include "task.h"

void vApplicationStackOverflowHook(TaskHandle_t xTask, char *pcTaskName)
{
    /* This function will be called if a task overflows its stack. pxCurrentTCB
    points to the task that has overflowed its stack. */
    ( void ) xTask;
    ( void ) pcTaskName;
    for(;;);
}

void vApplicationMallocFailedHook(void)
{
    /* This function will be called if a call to pvPortMalloc() fails to allocate
    enough memory. pvPortMalloc() is called internally by the kernel whenever a
    task, queue, timer, event group, or semaphore is created. */
    for(;;);
}

void vApplicationTickHook(void)
{
    /* This function will be called by each tick interrupt if
    configUSE_TICK_HOOK is set to 1 in FreeRTOSConfig.h. */
}

void vApplicationIdleHook(void)
{
    /* This function will be called on each iteration of the idle task when
    configUSE_IDLE_HOOK is set to 1 in FreeRTOSConfig.h. */
}
