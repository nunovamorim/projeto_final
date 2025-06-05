#include "protocol.h"
#include <string.h>

// CRC-16 CCITT table for polynomial 0x1021
static const uint16_t crc16_table[256] = {
    0x0000, 0x1021, 0x2042, 0x3063, 0x4084, 0x50A5, 0x60C6, 0x70E7,
    0x8108, 0x9129, 0xA14A, 0xB16B, 0xC18C, 0xD1AD, 0xE1CE, 0xF1EF,
    /* ... remaining table entries ... */
};

uint16_t calculate_crc16(const uint8_t *data, size_t length) {
    uint16_t crc = 0xFFFF; // Initial value
    
    for (size_t i = 0; i < length; i++) {
        crc = (crc << 8) ^ crc16_table[(crc >> 8) ^ data[i]];
    }
    
    return crc;
}

int validate_message(const MessageHeader *header, const uint8_t *data) {
    // Check sync bytes
    if (header->sync[0] != SYNC_BYTE1 || header->sync[1] != SYNC_BYTE2) {
        return ERR_INVALID_COMMAND;
    }
    
    // Calculate and verify checksum
    uint16_t calc_checksum = calculate_crc16(data, header->length);
    if (calc_checksum != header->checksum) {
        return ERR_INVALID_CHECKSUM;
    }
    
    return 0; // Success
}

int create_message(uint8_t type, uint8_t flags, const void *data, size_t data_length, uint8_t *buffer) {
    MessageHeader *header = (MessageHeader *)buffer;
    
    // Fill header
    header->sync[0] = SYNC_BYTE1;
    header->sync[1] = SYNC_BYTE2;
    header->type = type;
    header->flags = flags;
    header->length = data_length;
    
    // Copy data after header
    if (data_length > 0 && data != NULL) {
        memcpy(buffer + sizeof(MessageHeader), data, data_length);
    }
    
    // Calculate checksum on data portion
    header->checksum = calculate_crc16(buffer + sizeof(MessageHeader), data_length);
    
    return sizeof(MessageHeader) + data_length;
}

int process_message(const uint8_t *buffer, size_t length) {
    if (length < sizeof(MessageHeader)) {
        return ERR_INVALID_COMMAND;
    }
    
    const MessageHeader *header = (MessageHeader *)buffer;
    const uint8_t *data = buffer + sizeof(MessageHeader);
    
    // Validate message format and checksum
    int result = validate_message(header, data);
    if (result != 0) {
        return result;
    }
    
    // Process based on message type
    switch (header->type) {
        case MSG_TYPE_ADCS_CMD:
            if (header->length != sizeof(ADCSCommand)) {
                return ERR_INVALID_PARAMS;
            }
            // Process ADCS command
            break;
            
        case MSG_TYPE_TELEMETRY_REQ:
            // Handle telemetry request
            break;
            
        case MSG_TYPE_TELEMETRY_DATA:
            if (header->length != sizeof(TelemetryData)) {
                return ERR_INVALID_PARAMS;
            }
            // Process telemetry data
            break;
            
        case MSG_TYPE_ACK:
            // Process acknowledgment
            break;
            
        case MSG_TYPE_ERROR:
            // Process error message
            break;
            
        case MSG_TYPE_HEARTBEAT:
            // Process heartbeat
            break;
            
        default:
            return ERR_INVALID_COMMAND;
    }
    
    return 0;
}
