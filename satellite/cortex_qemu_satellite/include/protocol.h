#ifndef PROTOCOL_H
#define PROTOCOL_H

#include <stdint.h>
#include <stddef.h>

// Sync bytes
#define SYNC_BYTE1 0xAA
#define SYNC_BYTE2 0x55

// Message types
#define MSG_TYPE_ADCS_CMD         0x01
#define MSG_TYPE_TELEMETRY_REQ    0x02
#define MSG_TYPE_TELEMETRY_DATA   0x03
#define MSG_TYPE_ACK              0x04
#define MSG_TYPE_ERROR            0x05
#define MSG_TYPE_HEARTBEAT        0xFF

// Control flags
#define FLAG_REQUIRES_ACK         0x01
#define FLAG_FRAGMENTED          0x02
#define FLAG_LAST_FRAGMENT       0x04

// Error codes
#define ERR_INVALID_COMMAND      0x01
#define ERR_INVALID_CHECKSUM     0x02
#define ERR_TIMEOUT             0x03
#define ERR_INVALID_PARAMS      0x04
#define ERR_INVALID_STATE       0x05

// Estrutura do cabeçalho comum
typedef struct {
    uint8_t  sync[2];     // Bytes de sincronização (0xAA, 0x55)
    uint8_t  type;        // Tipo da mensagem
    uint8_t  flags;       // Flags de controle
    uint16_t length;      // Comprimento dos dados
    uint16_t checksum;    // CRC-16 dos dados
} MessageHeader;

// Estrutura de comando ADCS
typedef struct {
    float roll;    // Ângulo de rolagem desejado
    float pitch;   // Ângulo de arfagem desejado
    float yaw;     // Ângulo de guinada desejado
} ADCSCommand;

// Estrutura de dados de telemetria
typedef struct {
    uint32_t timestamp;     // Timestamp em milissegundos
    float    temperature;   // Temperatura em Celsius
    float    power;        // Consumo de energia em Watts
    float    battery;      // Nível da bateria em %
    struct {
        float roll;        // Ângulo atual de rolagem
        float pitch;       // Ângulo atual de arfagem
        float yaw;         // Ângulo atual de guinada
        uint8_t mode;      // Modo de controle ADCS
    } adcs;
} TelemetryData;

// Protótipos das funções
uint16_t calculate_crc16(const uint8_t *data, size_t length);
int validate_message(const MessageHeader *header, const uint8_t *data);
int create_message(uint8_t type, uint8_t flags, const void *data, size_t data_length, uint8_t *buffer);
int process_message(const uint8_t *buffer, size_t length);

#endif // PROTOCOL_H
