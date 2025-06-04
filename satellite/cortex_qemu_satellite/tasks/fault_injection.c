#include <string.h>
#include <stdlib.h>
#include "fault_injection.h"

// Armazena falhas ativas
static FaultInjection activeFaults[8];
static uint8_t numActiveFaults = 0;

BaseType_t xInjectFault(FaultInjection* fault)
{
    if (numActiveFaults >= 8 || fault == NULL)
        return pdFAIL;
    
    // Copiar configuração da falha
    memcpy(&activeFaults[numActiveFaults], fault, sizeof(FaultInjection));
    
    // Alocar memória para parâmetros se necessário
    if (fault->parameters != NULL)
    {
        switch (fault->type)
        {
            case FAULT_TASK_DELAY:
            case FAULT_TCP_DELAY:
                activeFaults[numActiveFaults].parameters = pvPortMalloc(sizeof(uint32_t));
                memcpy(activeFaults[numActiveFaults].parameters, fault->parameters, sizeof(uint32_t));
                break;
                
            case FAULT_CPU_OVERLOAD:
                activeFaults[numActiveFaults].parameters = pvPortMalloc(sizeof(uint8_t));
                memcpy(activeFaults[numActiveFaults].parameters, fault->parameters, sizeof(uint8_t));
                break;
                
            default:
                activeFaults[numActiveFaults].parameters = NULL;
                break;
        }
    }
    
    numActiveFaults++;
    return pdPASS;
}

void vClearFaults(void)
{
    for (uint8_t i = 0; i < numActiveFaults; i++)
    {
        if (activeFaults[i].parameters != NULL)
        {
            vPortFree(activeFaults[i].parameters);
        }
    }
    numActiveFaults = 0;
}

BaseType_t xCheckFault(FaultType type)
{
    for (uint8_t i = 0; i < numActiveFaults; i++)
    {
        if (activeFaults[i].type == type)
        {
            // Verificar probabilidade
            float random = (float)rand() / RAND_MAX;
            if (random < activeFaults[i].probability)
            {
                // Simular falha
                switch (type)
                {
                    case FAULT_TASK_DELAY:
                    case FAULT_TCP_DELAY:
                        if (activeFaults[i].parameters != NULL)
                        {
                            uint32_t delay = *(uint32_t*)activeFaults[i].parameters;
                            vTaskDelay(pdMS_TO_TICKS(delay));
                        }
                        break;
                        
                    case FAULT_TASK_HANG:
                        vTaskSuspend(NULL); // Suspende a task atual
                        break;
                        
                    case FAULT_MEMORY_LEAK:
                        pvPortMalloc(100); // Vazar 100 bytes
                        break;
                        
                    case FAULT_CPU_OVERLOAD:
                        if (activeFaults[i].parameters != NULL)
                        {
                            uint8_t load = *(uint8_t*)activeFaults[i].parameters;
                            for (uint8_t j = 0; j < load; j++)
                            {
                                // Gerar carga de CPU
                                volatile uint32_t dummy = 0;
                                for (uint32_t k = 0; k < 10000; k++)
                                {
                                    dummy += k;
                                }
                            }
                        }
                        break;
                        
                    default:
                        break;
                }
                return pdTRUE;
            }
        }
    }
    return pdFALSE;
}
