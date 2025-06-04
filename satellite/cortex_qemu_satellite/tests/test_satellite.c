#include "unity.h"
#include "main_so.h"
#include "tc_proc.h"
#include "adcs_proc.h"
#include "tm_proc.h"

void setUp(void)
{
    // Inicialização antes de cada teste
}

void tearDown(void)
{
    // Limpeza após cada teste
}

void test_ADCS_UpdateAttitude(void)
{
    float angles[3] = {1.0f, 2.0f, 3.0f};
    BaseType_t result;
    
    // Test normal operation
    result = xUpdateAttitude(angles);
    TEST_ASSERT_EQUAL(pdPASS, result);
    
    ADCSStatus status = xGetADCSStatus();
    TEST_ASSERT_FLOAT_WITHIN(0.1f, 1.0f, status.roll);
    TEST_ASSERT_FLOAT_WITHIN(0.1f, 2.0f, status.pitch);
    TEST_ASSERT_FLOAT_WITHIN(0.1f, 3.0f, status.yaw);
}

void test_TC_ProcessCommand(void)
{
    Command cmd;
    BaseType_t result;
    
    // Test ADCS command
    uint8_t cmdBuffer[] = {0x01, 0x00, 0x00, 0x80, 0x3F}; // Command type 1 with float value 1.0
    memcpy(commandBuffer, cmdBuffer, sizeof(cmdBuffer));
    
    result = xProcessCommand(&cmd);
    TEST_ASSERT_EQUAL(pdPASS, result);
    TEST_ASSERT_EQUAL(CMD_ADCS_CONTROL, cmd.type);
    
    float* params = (float*)cmd.parameters;
    TEST_ASSERT_FLOAT_WITHIN(0.1f, 1.0f, params[0]);
}

void test_TM_SendTelemetry(void)
{
    TelemetryPacket packet;
    BaseType_t result;
    
    packet.timestamp = xTaskGetTickCount();
    packet.temperature = 20.0f;
    packet.power = 100.0f;
    packet.battery_level = 95.0f;
    
    result = xSendTelemetry(&packet);
    TEST_ASSERT_EQUAL(pdPASS, result);
}

void test_TCP_Communication(void)
{
    TCPStatus status;
    uint8_t buffer[256];
    size_t received;
    
    // Test connection
    status = xTCPConnect("192.168.1.96", 5000);
    TEST_ASSERT_EQUAL(TCP_OK, status);
    
    // Test send
    const char* testData = "Test Message";
    status = xTCPSend(testData, strlen(testData));
    TEST_ASSERT_EQUAL(TCP_OK, status);
    
    // Test receive
    status = xTCPReceive(buffer, sizeof(buffer), &received);
    TEST_ASSERT_EQUAL(TCP_OK, status);
    
    vTCPDisconnect();
}

int main(void)
{
    UNITY_BEGIN();
    
    RUN_TEST(test_ADCS_UpdateAttitude);
    RUN_TEST(test_TC_ProcessCommand);
    RUN_TEST(test_TM_SendTelemetry);
    RUN_TEST(test_TCP_Communication);
    
    return UNITY_END();
}
