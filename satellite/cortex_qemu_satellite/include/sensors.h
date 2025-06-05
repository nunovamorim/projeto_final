#ifndef SENSORS_H
#define SENSORS_H

// Update simulated sensor values
void vUpdateSensorValues(void);

// Get current sensor values
void vGetSensorState(float *temperature, float *power, float *battery);

#endif // SENSORS_H
