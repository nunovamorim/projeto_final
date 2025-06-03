#include <stdio.h>
#include <string.h>
#include <stdlib.h>

/* FreeRTOS includes. */
#include "FreeRTOS.h"
#include "task.h"
#include "queue.h"
#include "semphr.h"
#include "event_groups.h"
#include "timers.h"

/* CMSIS includes (para acesso ao hardware simulado) */
#include "CMSIS/CMSDK_CM3.h"

/* Define de versão do sistema */
#define SATELLITE_OS_VERSION "1.0.0"

/* Socket server definitions */
#define GROUND_PORT 10000
#define MAX_CONNECTIONS 1

/* Definição das prioridades das tarefas */
#define MAIN_SO_PRIORITY     (configMAX_PRIORITIES - 1) /* Máxima prioridade */
#define TC_PROC_PRIORITY     (configMAX_PRIORITIES - 2) /* Alta prioridade */
#define ADCS_PROC_PRIORITY   (configMAX_PRIORITIES - 3) /* Média prioridade */
#define TM_PROC_PRIORITY     (configMAX_PRIORITIES - 4) /* Baixa prioridade */

/* Tamanhos dos stacks (em palavras, não bytes) */
#define MAIN_SO_STACK_SIZE   (configMINIMAL_STACK_SIZE * 2)
#define TC_PROC_STACK_SIZE   (configMINIMAL_STACK_SIZE * 2)
#define ADCS_PROC_STACK_SIZE (configMINIMAL_STACK_SIZE * 2)
#define TM_PROC_STACK_SIZE   (configMINIMAL_STACK_SIZE * 2)

/* Tamanho das filas de mensagens */
#define TC_QUEUE_SIZE        10
#define TM_QUEUE_SIZE        10
#define ADCS_QUEUE_SIZE      5

/* Códigos de comando (telecontrole) */
typedef enum {
    CMD_NOP = 0,         /* No operation */
    CMD_RESET = 1,       /* Reset subsistema */
    CMD_ADCS_SET = 2,    /* Define orientação do ADCS */
    CMD_GET_TELEMETRY = 3,/* Solicita telemetria */
    CMD_SET_PARAM = 4,   /* Define parâmetro */
    CMD_SHUTDOWN = 5     /* Desligamento subsistema */
} CommandCode_t;

/* Estrutura para comandos */
typedef struct {
    CommandCode_t code;          /* Código do comando */
    uint32_t param1;             /* Parâmetro 1 */
    uint32_t param2;             /* Parâmetro 2 */
    float fParam;                /* Parâmetro float */
    uint8_t checksum;            /* Checksum para validação */
} Command_t;

/* Estrutura para dados do satélite */
typedef struct {
    float attitude[3];      /* Roll, Pitch, Yaw em graus */
    float position[3];      /* Posição X, Y, Z (simulada) */
    uint32_t temperature;   /* Temperatura do sistema em graus C */
    uint32_t power_level;   /* Nível de bateria (0-100%) */
    uint8_t system_status;  /* Status do sistema: 0=erro, 1=nominal, 2=alerta */
    TickType_t timestamp;   /* Timestamp em ticks */
} SatelliteData_t;

/* Handles para as tarefas */
static TaskHandle_t xMainSOHandle;
static TaskHandle_t xTCProcHandle;
static TaskHandle_t xADCSProcHandle;
static TaskHandle_t xTMProcHandle;

/* Filas para comunicação entre tarefas */
static QueueHandle_t xTCQueue;   /* Fila de telecomandos recebidos */
static QueueHandle_t xTMQueue;   /* Fila de telemetria para envio */
static QueueHandle_t xADCSQueue; /* Fila de comandos para ADCS */

/* Mutex para acesso a recursos compartilhados */
static SemaphoreHandle_t xResourceMutex;

/* Grupo de eventos para sincronização */
static EventGroupHandle_t xSystemEvents;

/* Bits de eventos */
#define EVENT_TC_RECEIVED    (1 << 0)
#define EVENT_TM_READY       (1 << 1)
#define EVENT_ADCS_UPDATE    (1 << 2)
#define EVENT_ERROR          (1 << 3)

/* Dados globais do satélite - protegidos por mutex */
static SatelliteData_t xSatelliteData;

/* Buffer para estatísticas de runtime */
static char pcStatBuffer[512];

/* Protótipos das tarefas */
static void prvMainSOTask(void *pvParameters);
static void prvTCProcTask(void *pvParameters);
static void prvADCSProcTask(void *pvParameters);
static void prvTMProcTask(void *pvParameters);
static void prvSocketServerTask(void *pvParameters);  /* New socket server task */

/* Função auxiliar para calcular checksum */
static uint8_t prvCalculateChecksum(const Command_t *cmd) {
    uint8_t checksum = 0;
    checksum ^= cmd->code;
    checksum ^= (cmd->param1 & 0xFF);
    checksum ^= ((cmd->param1 >> 8) & 0xFF);
    checksum ^= ((cmd->param1 >> 16) & 0xFF);
    checksum ^= ((cmd->param1 >> 24) & 0xFF);
    checksum ^= (cmd->param2 & 0xFF);
    checksum ^= ((cmd->param2 >> 8) & 0xFF);
    checksum ^= ((cmd->param2 >> 16) & 0xFF);
    checksum ^= ((cmd->param2 >> 24) & 0xFF);
    
    /* Conversão float-to-bytes simplificada para checksum */
    uint32_t fAsInt = *(uint32_t*)&cmd->fParam;
    checksum ^= (fAsInt & 0xFF);
    checksum ^= ((fAsInt >> 8) & 0xFF);
    checksum ^= ((fAsInt >> 16) & 0xFF);
    checksum ^= ((fAsInt >> 24) & 0xFF);
    
    return checksum;
}

/* Função auxiliar para validar checksum de comandos */
static BaseType_t prvValidateCommand(const Command_t *cmd) {
    uint8_t calculatedChecksum = prvCalculateChecksum(cmd);
    return (calculatedChecksum == cmd->checksum) ? pdTRUE : pdFALSE;
}

/*-----------------------------------------------------------*/
/* MAIN_SO - Sistema Operativo Principal */
static void prvMainSOTask(void *pvParameters) {
    /* Variáveis para controle de tempo */
    TickType_t xLastWakeTime;
    const TickType_t xMainSOPeriod = pdMS_TO_TICKS(100); /* 100ms */
    
    /* Para monitoramento de stack */
    UBaseType_t uxHighWaterMark;
    
    /* Inicializa o timestamp para execução periódica */
    xLastWakeTime = xTaskGetTickCount();
    
    /* Estado inicial do satélite */
    if (xSemaphoreTake(xResourceMutex, pdMS_TO_TICKS(10)) == pdTRUE) {
        xSatelliteData.system_status = 1; /* Nominal */
        xSatelliteData.power_level = 100; /* Bateria 100% */
        xSatelliteData.temperature = 20;  /* Temperatura inicial 20°C */
        xSemaphoreGive(xResourceMutex);
    }
    
    printf("Satellite OS v%s inicializado\n", SATELLITE_OS_VERSION);
    printf("MAIN_SO: Tarefa iniciada com prioridade %ld\n", (long)uxTaskPriorityGet(NULL));
    
    /* Loop principal */
    for (;;) {
        /* Monitorar o sistema e processar comandos pendentes */
        if (xSemaphoreTake(xResourceMutex, pdMS_TO_TICKS(10)) == pdTRUE) {
            /* Simular consumo de energia */
            if (xSatelliteData.power_level > 0) {
                xSatelliteData.power_level--;
            }
            
            /* Simular variações na temperatura */
            xSatelliteData.temperature = 20 + (rand() % 5);
            
            /* Atualizar timestamp */
            xSatelliteData.timestamp = xTaskGetTickCount();
            
            xSemaphoreGive(xResourceMutex);
        }
        
        /* A cada 10 segundos, exibir estatísticas de runtime */
        if ((xTaskGetTickCount() % pdMS_TO_TICKS(10000)) < 100) {
            printf("\n==== Estatísticas de Runtime ====\n");
            
            /* Formatar e exibir estatísticas de tarefas */
            vTaskList(pcStatBuffer);
            printf("Task\t\tState\tPrio\tStack\tNum\n");
            printf("========================================\n");
            printf("%s\n", pcStatBuffer);
            
            /* Exibir estatísticas de utilização de CPU */
            vTaskGetRunTimeStats(pcStatBuffer);
            printf("\nTask\t\tAbs Time\t%% Time\n");
            printf("========================================\n");
            printf("%s\n", pcStatBuffer);
            
            /* Verificar o maior uso de stack (high water mark) */
            uxHighWaterMark = uxTaskGetStackHighWaterMark(NULL);
            printf("MAIN_SO Stack High Water Mark: %lu words\n", (unsigned long)uxHighWaterMark);
            
            uxHighWaterMark = uxTaskGetStackHighWaterMark(xTCProcHandle);
            printf("TC_Proc Stack High Water Mark: %lu words\n", (unsigned long)uxHighWaterMark);
            
            uxHighWaterMark = uxTaskGetStackHighWaterMark(xADCSProcHandle);
            printf("ADCS_Proc Stack High Water Mark: %lu words\n", (unsigned long)uxHighWaterMark);
            
            uxHighWaterMark = uxTaskGetStackHighWaterMark(xTMProcHandle);
            printf("TM_Proc Stack High Water Mark: %lu words\n", (unsigned long)uxHighWaterMark);
            
            printf("==================================\n\n");
        }
        
        /* Aguardar o próximo ciclo de execução */
        vTaskDelayUntil(&xLastWakeTime, xMainSOPeriod);
    }
}

/*-----------------------------------------------------------*/
/* TC_Proc - Processamento de Telecomandos */
static void prvTCProcTask(void *pvParameters) {
    Command_t xReceivedCommand;
    uint32_t ulCommandCounter = 0;
    TickType_t xCommandReceiveTime;
    
    printf("TC_Proc: Tarefa iniciada com prioridade %ld\n", (long)uxTaskPriorityGet(NULL));
    
    for (;;) {
        /* Esperar por um comando na fila TC */
        if (xQueueReceive(xTCQueue, &xReceivedCommand, portMAX_DELAY) == pdPASS) {
            xCommandReceiveTime = xTaskGetTickCount();
            ulCommandCounter++;
            
            /* Validar checksum do comando */
            if (prvValidateCommand(&xReceivedCommand)) {
                printf("TC_Proc: Comando válido recebido: Código = %d\n", xReceivedCommand.code);
                
                /* Processar o comando com base no código */
                switch (xReceivedCommand.code) {
                    case CMD_NOP:
                        /* Comando NOP - não faz nada */
                        printf("TC_Proc: Comando NOP processado\n");
                        break;
                        
                    case CMD_RESET:
                        /* Comando para redefinir subsistema */
                        printf("TC_Proc: Comando RESET subsistema %lu\n", (unsigned long)xReceivedCommand.param1);
                        /* Notificar o subsistema apropriado */
                        if (xReceivedCommand.param1 == 2) { /* ADCS */
                            /* Enviar comando para redefinir ADCS */
                            if (xQueueSend(xADCSQueue, &xReceivedCommand, pdMS_TO_TICKS(10)) != pdPASS) {
                                printf("TC_Proc: ERRO - Fila ADCS cheia!\n");
                            }
                        }
                        break;
                        
                    case CMD_ADCS_SET:
                        /* Comando para configurar orientação ADCS */
                        printf("TC_Proc: Comando SET ADCS - fParam = %.2f\n", xReceivedCommand.fParam);
                        if (xQueueSend(xADCSQueue, &xReceivedCommand, pdMS_TO_TICKS(10)) != pdPASS) {
                            printf("TC_Proc: ERRO - Fila ADCS cheia!\n");
                        }
                        break;
                        
                    case CMD_GET_TELEMETRY:
                        /* Comando para solicitar telemetria */
                        printf("TC_Proc: Comando GET_TELEMETRY recebido\n");
                        /* Sinalizar evento para TM_Proc enviar telemetria */
                        xEventGroupSetBits(xSystemEvents, EVENT_TM_READY);
                        break;
                        
                    default:
                        printf("TC_Proc: Comando desconhecido: %d\n", xReceivedCommand.code);
                        break;
                }
                
                /* Registrar latência no processamento do comando */
                TickType_t xCommandProcessTime = xTaskGetTickCount() - xCommandReceiveTime;
                printf("TC_Proc: Tempo de processamento do comando: %lu ms\n", 
                       (unsigned long)(xCommandProcessTime * portTICK_PERIOD_MS));
                
            } else {
                printf("TC_Proc: ERRO - Checksum inválido no comando recebido!\n");
            }
        }
    }
}

/*-----------------------------------------------------------*/
/* ADCS_Proc - Determinação e Controle de Atitude */
static void prvADCSProcTask(void *pvParameters) {
    Command_t xCommand;
    TickType_t xLastWakeTime;
    const TickType_t xADCSPeriod = pdMS_TO_TICKS(200); /* 200ms */
    
    /* Valores iniciais de atitude (roll, pitch, yaw) */
    float currentAttitude[3] = {0.0f, 0.0f, 0.0f};
    float targetAttitude[3] = {0.0f, 0.0f, 0.0f};
    
    /* Inicialização */
    xLastWakeTime = xTaskGetTickCount();
    printf("ADCS_Proc: Tarefa iniciada com prioridade %ld\n", (long)uxTaskPriorityGet(NULL));
    
    for (;;) {
        /* Verificar se há comandos na fila ADCS */
        if (xQueueReceive(xADCSQueue, &xCommand, 0) == pdPASS) {
            /* Processar comandos ADCS */
            switch (xCommand.code) {
                case CMD_RESET:
                    printf("ADCS_Proc: Redefinindo parâmetros ADCS\n");
                    targetAttitude[0] = 0.0f;
                    targetAttitude[1] = 0.0f;
                    targetAttitude[2] = 0.0f;
                    break;
                    
                case CMD_ADCS_SET:
                    /* Definir nova orientação alvo */
                    printf("ADCS_Proc: Nova orientação alvo = %.2f graus\n", xCommand.fParam);
                    targetAttitude[0] = xCommand.fParam;
                    targetAttitude[1] = xCommand.fParam * 0.5f;
                    targetAttitude[2] = xCommand.fParam * 0.25f;
                    break;
                    
                default:
                    printf("ADCS_Proc: Comando não reconhecido: %d\n", xCommand.code);
                    break;
            }
        }
        
        /* Simular a convergência para orientação alvo (controle simplificado) */
        for (int i = 0; i < 3; i++) {
            /* Diferença entre alvo e atual */
            float diff = targetAttitude[i] - currentAttitude[i];
            
            /* Movimento em direção ao alvo */
            if (fabsf(diff) < 0.1f) {
                currentAttitude[i] = targetAttitude[i];
            } else {
                currentAttitude[i] += (diff * 0.1f); /* Convergência gradual */
            }
            
            /* Normalizar ângulos para 0-360 graus */
            while (currentAttitude[i] >= 360.0f) {
                currentAttitude[i] -= 360.0f;
            }
            while (currentAttitude[i] < 0.0f) {
                currentAttitude[i] += 360.0f;
            }
        }
        
        /* Atualizar os dados do satélite com a nova atitude */
        if (xSemaphoreTake(xResourceMutex, pdMS_TO_TICKS(10)) == pdTRUE) {
            memcpy(xSatelliteData.attitude, currentAttitude, sizeof(currentAttitude));
            xSemaphoreGive(xResourceMutex);
            
            /* Sinalizar que houve atualização ADCS */
            xEventGroupSetBits(xSystemEvents, EVENT_ADCS_UPDATE);
        }
        
        /* Aguardar próximo ciclo */
        vTaskDelayUntil(&xLastWakeTime, xADCSPeriod);
    }
}

/*-----------------------------------------------------------*/
/* TM_Proc - Processamento de Telemetria */
static void prvTMProcTask(void *pvParameters) {
    SatelliteData_t xLocalData;
    TickType_t xLastWakeTime;
    const TickType_t xTMPeriod = pdMS_TO_TICKS(1000); /* 1 segundo */
    EventBits_t xEventBits;
    
    /* Inicialização */
    xLastWakeTime = xTaskGetTickCount();
    printf("TM_Proc: Tarefa iniciada com prioridade %ld\n", (long)uxTaskPriorityGet(NULL));
    
    for (;;) {
        /* Aguardar evento TM_READY ou timeout */
        xEventBits = xEventGroupWaitBits(
            xSystemEvents,
            EVENT_TM_READY | EVENT_ADCS_UPDATE,
            pdTRUE,  /* Limpar bits ao retornar */
            pdFALSE, /* Qualquer bit ativa */
            xTMPeriod); /* Timeout para envio periódico */
            
        /* Obter dados do satélite */
        if (xSemaphoreTake(xResourceMutex, pdMS_TO_TICKS(10)) == pdTRUE) {
            /* Copiar dados para uso local */
            memcpy(&xLocalData, &xSatelliteData, sizeof(SatelliteData_t));
            xSemaphoreGive(xResourceMutex);
            
            /* Enviar telemetria */
            printf("\n--- Telemetria do Satélite ---\n");
            printf("Timestamp: %lu\n", (unsigned long)xLocalData.timestamp);
            printf("Atitude (RPY): %.2f, %.2f, %.2f\n", 
                   xLocalData.attitude[0], xLocalData.attitude[1], xLocalData.attitude[2]);
            printf("Temperatura: %lu°C\n", (unsigned long)xLocalData.temperature);
            printf("Nível de Energia: %lu%%\n", (unsigned long)xLocalData.power_level);
            printf("Status do Sistema: %s\n", 
                   xLocalData.system_status == 1 ? "NOMINAL" : 
                   xLocalData.system_status == 2 ? "ALERTA" : "ERRO");
            printf("----------------------------\n");
            
            /* Simular envio para Ground Station */
            if (xEventBits & EVENT_TM_READY) {
                printf("TM_Proc: Telemetria enviada em resposta a comando\n");
            } else if (xEventBits & EVENT_ADCS_UPDATE) {
                printf("TM_Proc: Telemetria enviada após atualização ADCS\n");
            } else {
                printf("TM_Proc: Telemetria periódica enviada\n");
            }
            
            /* Colocar dados na fila de telemetria para outros usos */
            if (xQueueSend(xTMQueue, &xLocalData, 0) != pdPASS) {
                /* Se a fila estiver cheia, remover item antigo e tentar novamente */
                SatelliteData_t xDummy;
                xQueueReceive(xTMQueue, &xDummy, 0);
                xQueueSend(xTMQueue, &xLocalData, 0);
            }
        } else {
            printf("TM_Proc: ERRO - Não foi possível obter mutex\n");
        }
        
        /* Aguardar próximo ciclo */
        vTaskDelayUntil(&xLastWakeTime, xTMPeriod);
    }
}

/*-----------------------------------------------------------*/
/* Socket Server Task - Handles communications with Ground Station */
#if defined(__unix__) || defined(__APPLE__)
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h> /* for close() */

static void prvSocketServerTask(void *pvParameters) {
    int server_fd, client_fd;
    struct sockaddr_in address;
    int opt = 1;
    int addrlen = sizeof(address);
    uint8_t buffer[256];
    
    printf("Socket Server: Task started with priority %ld\n", (long)uxTaskPriorityGet(NULL));
    
    // Create socket file descriptor
    if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
        printf("Socket Server: Error creating socket\n");
        vTaskDelete(NULL);
        return;
    }
    
    // Set socket options
    if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR | SO_REUSEPORT, &opt, sizeof(opt))) {
        printf("Socket Server: Error setting socket options\n");
        close(server_fd);
        vTaskDelete(NULL);
        return;
    }
    
    // Setup address structure
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(GROUND_PORT);
    
    // Bind socket to port
    if (bind(server_fd, (struct sockaddr *)&address, sizeof(address)) < 0) {
        printf("Socket Server: Error binding socket\n");
        close(server_fd);
        vTaskDelete(NULL);
        return;
    }
    
    // Listen for connections
    if (listen(server_fd, MAX_CONNECTIONS) < 0) {
        printf("Socket Server: Error listening\n");
        close(server_fd);
        vTaskDelete(NULL);
        return;
    }
    
    printf("Socket Server: Started on port %d\n", GROUND_PORT);
    
    for (;;) {
        // Accept incoming connection
        printf("Socket Server: Waiting for ground station connection...\n");
        client_fd = accept(server_fd, (struct sockaddr *)&address, (socklen_t*)&addrlen);
        if (client_fd < 0) {
            printf("Socket Server: Error accepting connection\n");
            vTaskDelay(pdMS_TO_TICKS(5000)); // Wait before trying again
            continue;
        }
        
        printf("Socket Server: Ground station connected!\n");
        
        // Handle client communication
        while (1) {
            // Set non-blocking with timeout to avoid hanging
            fd_set readset;
            struct timeval tv;
            FD_ZERO(&readset);
            FD_SET(client_fd, &readset);
            tv.tv_sec = 0;
            tv.tv_usec = 100000; // 100ms timeout
            
            int activity = select(client_fd+1, &readset, NULL, NULL, &tv);
            
            if (activity < 0) {
                printf("Socket Server: Select error\n");
                break;
            }
            
            // Check if we have data to read
            if (activity > 0 && FD_ISSET(client_fd, &readset)) {
                // Receive command
                int bytes_read = recv(client_fd, buffer, sizeof(buffer), 0);
                
                if (bytes_read <= 0) {
                    printf("Socket Server: Ground station disconnected\n");
                    break;
                }
                
                // Process command
                if (bytes_read > 2 && buffer[0] == 0xAA) {
                    Command_t cmd;
                    cmd.code = buffer[1];
                    
                    if (bytes_read >= 15) { // Check we have enough data
                        cmd.param1 = *((uint32_t*)&buffer[3]);
                        cmd.param2 = *((uint32_t*)&buffer[7]);
                        cmd.fParam = *((float*)&buffer[11]);
                        cmd.checksum = buffer[bytes_read - 1];
                        
                        // Validate and send to command queue
                        if (prvValidateCommand(&cmd)) {
                            if (xQueueSend(xTCQueue, &cmd, pdMS_TO_TICKS(10)) != pdPASS) {
                                printf("Socket Server: Command queue full\n");
                            } else {
                                printf("Socket Server: Command received and queued (Code: %d)\n", cmd.code);
                            }
                        } else {
                            printf("Socket Server: Invalid command checksum\n");
                        }
                    } else {
                        printf("Socket Server: Command packet too short\n");
                    }
                }
            }
            
            // Send telemetry if available
            SatelliteData_t tlm;
            if (xQueueReceive(xTMQueue, &tlm, 0) == pdPASS) {
                uint8_t tlm_packet[64] = {0};
                
                // Telemetry header
                tlm_packet[0] = 0xBB;  // Header
                tlm_packet[1] = 0x01;  // Telemetry ID
                tlm_packet[2] = sizeof(SatelliteData_t) + 7; // Length
                
                // Copy timestamp (4 bytes)
                memcpy(&tlm_packet[3], &tlm.timestamp, sizeof(TickType_t));
                
                // Copy payload
                memcpy(&tlm_packet[7], &tlm, sizeof(SatelliteData_t));
                
                // Status byte
                tlm_packet[7 + sizeof(SatelliteData_t)] = tlm.system_status;
                
                // Calculate checksum
                uint8_t checksum = 0;
                for (int i = 0; i < 7 + sizeof(SatelliteData_t); i++) {
                    checksum ^= tlm_packet[i];
                }
                tlm_packet[7 + sizeof(SatelliteData_t) + 1] = checksum;
                
                // Send telemetry
                if (send(client_fd, tlm_packet, 7 + sizeof(SatelliteData_t) + 2, 0) < 0) {
                    printf("Socket Server: Error sending telemetry\n");
                } else {
                    printf("Socket Server: Telemetry sent to ground station\n");
                }
            }
            
            vTaskDelay(pdMS_TO_TICKS(100));  // Limit socket polling rate
        }
        
        close(client_fd);
        printf("Socket Server: Connection closed, waiting for new connection\n");
    }
    
    // Should never get here, but just in case
    close(server_fd);
    vTaskDelete(NULL);
}
#else
/* Dummy implementation for non-POSIX systems */
static void prvSocketServerTask(void *pvParameters) {
    printf("Socket Server: Socket communication not available on this platform\n");
    vTaskDelete(NULL);
}
#endif

/*-----------------------------------------------------------*/
/* Função auxiliar para gerar comandos de teste */
static void prvGenerateTestCommand(void) {
    static uint32_t ulTestCounter = 0;
    Command_t xCommand;
    
    ulTestCounter++;
    
    /* Variar comandos de teste */
    switch (ulTestCounter % 4) {
        case 0:
            xCommand.code = CMD_NOP;
            xCommand.param1 = 0;
            xCommand.param2 = 0;
            xCommand.fParam = 0.0f;
            break;
            
        case 1:
            xCommand.code = CMD_ADCS_SET;
            xCommand.param1 = ulTestCounter;
            xCommand.param2 = 0;
            xCommand.fParam = (float)(ulTestCounter % 360); /* Rotação de 0-359 */
            break;
            
        case 2:
            xCommand.code = CMD_GET_TELEMETRY;
            xCommand.param1 = ulTestCounter;
            xCommand.param2 = 0;
            xCommand.fParam = 0.0f;
            break;
            
        case 3:
            xCommand.code = CMD_RESET;
            xCommand.param1 = 2; /* ADCS subsystem */
            xCommand.param2 = 0;
            xCommand.fParam = 0.0f;
            break;
    }
    
    /* Calcular checksum */
    xCommand.checksum = prvCalculateChecksum(&xCommand);
    
    /* Enviar comando */
    printf("TEST: Enviando comando de teste CODE=%d\n", xCommand.code);
    if (xQueueSend(xTCQueue, &xCommand, pdMS_TO_TICKS(10)) != pdPASS) {
        printf("TEST: ERRO - Fila de comandos cheia!\n");
    }
}

/*-----------------------------------------------------------*/
/* Função para iniciar as estatísticas do runtime */
#if configGENERATE_RUN_TIME_STATS
static uint32_t ulRunTimeStatsClock = 0;

void vConfigureTimerForRunTimeStats(void) {
    ulRunTimeStatsClock = 0;
}

unsigned long ulGetRunTimeCounterValue(void) {
    return ulRunTimeStatsClock++;
}
#endif

/*-----------------------------------------------------------*/
/* Função chamada quando uma asserção falha */
void vAssertCalled(const char *pcFile, uint32_t ulLine) {
    volatile uint32_t ulSetToNonZeroToExit = 0;

    /* Parâmetros não usados - para evitar warnings */
    (void)pcFile;

    taskENTER_CRITICAL();
    {
        /* Exibir informações da asserção */
        printf("ERRO: Falha de asserção na linha %lu\n", (unsigned long)ulLine);
        printf("Arquivo: %s\n", pcFile);
        
        /* Loop para permitir debug em caso de falha */
        while (ulSetToNonZeroToExit == 0) {
            /* Loop infinito - só sai em debug ou reset */
        }
    }
    taskEXIT_CRITICAL();
}

/*-----------------------------------------------------------*/
/* Hook para falha na alocação de memória */
void vApplicationMallocFailedHook(void) {
    printf("ERRO CRITICO: Falha na alocação de memória!\n");
    configASSERT(0);
}

/*-----------------------------------------------------------*/
/* Hook para stack overflow */
void vApplicationStackOverflowHook(TaskHandle_t pxTask, char *pcTaskName) {
    (void)pxTask;
    printf("ERRO CRITICO: Stack overflow na tarefa %s!\n", pcTaskName);
    configASSERT(0);
}

/*-----------------------------------------------------------*/
/* Hook de tick (executa a cada tick do RTOS) */
void vApplicationTickHook(void) {
    static uint32_t ulTickCount = 0;
    
    /* Gerar comando de teste a cada 5 segundos */
    ulTickCount++;
    if (ulTickCount >= pdMS_TO_TICKS(5000)) {
        ulTickCount = 0;
        
        /* Gerar comando de teste periodicamente */
        prvGenerateTestCommand();
    }
}

/*-----------------------------------------------------------*/
int main(void) {
    printf("\n\n==================================\n");
    printf("Inicializando Sistema de Satélite\n");
    printf("==================================\n\n");
    
    /* Inicializar sementes aleatórias */
    srand((unsigned int)time(NULL));
    
    /* Criar filas de comunicação entre tarefas */
    xTCQueue = xQueueCreate(TC_QUEUE_SIZE, sizeof(Command_t));
    configASSERT(xTCQueue != NULL);
    
    xTMQueue = xQueueCreate(TM_QUEUE_SIZE, sizeof(SatelliteData_t));
    configASSERT(xTMQueue != NULL);
    
    xADCSQueue = xQueueCreate(ADCS_QUEUE_SIZE, sizeof(Command_t));
    configASSERT(xADCSQueue != NULL);
    
    /* Criar mutex para recursos compartilhados */
    xResourceMutex = xSemaphoreCreateMutex();
    configASSERT(xResourceMutex != NULL);
    
    /* Criar grupo de eventos */
    xSystemEvents = xEventGroupCreate();
    configASSERT(xSystemEvents != NULL);
    
    /* Criar as tarefas */
    xTaskCreate(prvMainSOTask, "MAIN_SO", MAIN_SO_STACK_SIZE, NULL, 
                MAIN_SO_PRIORITY, &xMainSOHandle);
                
    xTaskCreate(prvTCProcTask, "TC_PROC", TC_PROC_STACK_SIZE, NULL, 
                TC_PROC_PRIORITY, &xTCProcHandle);
                
    xTaskCreate(prvADCSProcTask, "ADCS_PROC", ADCS_PROC_STACK_SIZE, NULL, 
                ADCS_PROC_PRIORITY, &xADCSProcHandle);
                
    xTaskCreate(prvTMProcTask, "TM_PROC", TM_PROC_STACK_SIZE, NULL, 
                TM_PROC_PRIORITY, &xTMProcHandle);
    
    xTaskCreate(prvSocketServerTask, "SOCKET_SERVER", configMINIMAL_STACK_SIZE, NULL, 
                tskIDLE_PRIORITY, NULL);
    
    /* Iniciar o scheduler */
    vTaskStartScheduler();
    
    /* O programa só chega aqui se não houver memória suficiente */
    printf("ERRO FATAL: Falha ao iniciar o scheduler!\n");
    return 1;
}
