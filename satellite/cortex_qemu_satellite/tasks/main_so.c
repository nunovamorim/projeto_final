#include <string.h>
#include <stdio.h>
#include "main_so.h"
#include "tc_proc.h"
#include "adcs_proc.h"
#include "tm_proc.h"

// Contador para watchdog
static volatile uint32_t watchdogCounters[4] = {0};
static const uint32_t WATCHDOG_TIMEOUT = 5000; // 5 segundos em ticks

void vMainSOTask(void *pvParameters)
{
    Command command;
    BaseType_t status;

    // Inicializar contadores de watchdog
    for(int i = 0; i < 4; i++) {
        watchdogCounters[i] = xTaskGetTickCount();
    }

    // Task main loop
    for(;;)
    {
        // Verificar se há comandos pendentes
        status = xQueueReceive(xCommandQueue, &command, pdMS_TO_TICKS(100));
        
        if(status == pdPASS)
        {
            // Processar comando recebido
            switch(command.type)
            {
                case CMD_ADCS_CONTROL:
                    if(xSemaphoreTake(xResourceMutex, portMAX_DELAY) == pdTRUE)
                    {
                        // Atualizar atitude do satélite
                        status = xUpdateAttitude((float*)command.parameters);
                        xSemaphoreGive(xResourceMutex);
                        
                        // Liberar memória do comando
                        if(command.parameters != NULL)
                        {
                            vPortFree(command.parameters);
                        }
                    }
                    break;

                case CMD_TELEMETRY_REQUEST:
                    // Solicitar telemetria atualizada
                    if(xSemaphoreTake(xResourceMutex, portMAX_DELAY) == pdTRUE)
                    {
                        TelemetryPacket packet;
                        ADCSStatus adcsStatus = xGetADCSStatus();
                        
                        // Preencher pacote de telemetria
                        packet.timestamp = xTaskGetTickCount();
                        packet.adcs_status = adcsStatus;
                        
                        // Enviar telemetria
                        xSendTelemetry(&packet);
                        xSemaphoreGive(xResourceMutex);
                    }
                    break;

                default:
                    // Comando desconhecido
                    break;
            }
        }

        // Monitorar watchdog das tasks
        watchdogCounters[0]++; // MAIN_SO

        // Verificar outras tasks
        if(xTaskGetTickCount() - watchdogCounters[1] > WATCHDOG_TIMEOUT)
        {
            // TC_proc não está respondendo
            vTaskDelete(xTCProcHandle);
            xTaskCreate(vTCProcTask, "TC_PROC", configMINIMAL_STACK_SIZE * 2,
                       NULL, TC_PROC_PRIORITY, &xTCProcHandle);
        }

        if(xTaskGetTickCount() - watchdogCounters[2] > WATCHDOG_TIMEOUT)
        {
            // ADCS_proc não está respondendo
            vTaskDelete(xADCSProcHandle);
            xTaskCreate(vADCSProcTask, "ADCS_PROC", configMINIMAL_STACK_SIZE * 2,
                       NULL, ADCS_PROC_PRIORITY, &xADCSProcHandle);
        }

        if(xTaskGetTickCount() - watchdogCounters[3] > WATCHDOG_TIMEOUT)
        {
            // TM_proc não está respondendo
            vTaskDelete(xTMProcHandle);
            xTaskCreate(vTMProcTask, "TM_PROC", configMINIMAL_STACK_SIZE * 2,
                       NULL, TM_PROC_PRIORITY, &xTMProcHandle);
        }

        // Delay para não sobrecarregar o processador
        vTaskDelay(pdMS_TO_TICKS(10));
    }
}

// Funções para atualização do watchdog
void vUpdateTaskWatchdog(uint8_t taskId)
{
    if(taskId < 4)
    {
        watchdogCounters[taskId] = xTaskGetTickCount();
    }
}
