#include <stdlib.h>
#include <time.h>
#include <math.h>
#include "sensors.h"

// Simulated sensor values
static float g_temperature = 25.0f;
static float g_power = 10.0f;
static float g_battery = 100.0f;

// Update sensor values with some random variations
void vUpdateSensorValues(void)
{
    // Add random variations to temperature (-0.5 to +0.5)
    g_temperature += ((float)rand() / RAND_MAX - 0.5f);
    
    // Keep temperature in reasonable range (20-30°C)
    if (g_temperature < 20.0f) g_temperature = 20.0f;
    if (g_temperature > 30.0f) g_temperature = 30.0f;
    
    // Simulate power consumption (8-12W)
    g_power = 10.0f + ((float)rand() / RAND_MAX * 4.0f - 2.0f);
    
    // Simulate battery discharge
    g_battery -= 0.01f;
    if (g_battery < 0.0f) g_battery = 100.0f;  // Reset when empty
}

// Get current sensor values
void vGetSensorState(float *temperature, float *power, float *battery)
{
    *temperature = g_temperature;
    *power = g_power;
    *battery = g_battery;
}
