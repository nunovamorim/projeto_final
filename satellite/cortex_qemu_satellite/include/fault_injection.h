#ifndef FAULT_INJECTION_H
#define FAULT_INJECTION_H

#include "FreeRTOS.h"
#include "task.h"

// Tipos de falhas que podem ser simuladas
typedef enum {
    FAULT_NONE = 0,
    FAULT_TASK_DELAY,      // Atrasa a execução da task
    FAULT_TASK_HANG,       // Simula travamento da task
    FAULT_MEMORY_LEAK,     // Simula vazamento de memória
    FAULT_TCP_DROP,        // Descarta pacotes TCP
    FAULT_TCP_DELAY,       // Atrasa pacotes TCP
    FAULT_CPU_OVERLOAD,    // Simula sobrecarga de CPU
    FAULT_ADCS_ERROR       // Simula erro no ADCS
} FaultType;

// Estrutura para configurar a injeção de falhas
typedef struct {
    FaultType type;
    uint32_t duration;     // Duração da falha em ticks
    float probability;     // Probabilidade de ocorrência (0.0-1.0)
    void* parameters;      // Parâmetros específicos da falha
} FaultInjection;

// Funções de injeção de falhas
BaseType_t xInjectFault(FaultInjection* fault);
void vClearFaults(void);
BaseType_t xCheckFault(FaultType type);

#endif /* FAULT_INJECTION_H */
