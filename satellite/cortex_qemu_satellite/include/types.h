#ifndef TYPES_H
#define TYPES_H

#include <stdint.h>

// Command message structure
typedef struct {
    uint8_t type;
    uint8_t flags;
    uint16_t length;
    uint8_t data[256];
} CommandMessage;

// Telemetry message structure
typedef struct {
    uint32_t timestamp;
    float temperature;
    float power;
    float battery;
    struct {
        float roll;
        float pitch;
        float yaw;
        uint8_t mode;
    } adcs;
} TelemetryMessage;

#endif // TYPES_H
