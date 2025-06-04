#ifndef FREERTOS_IP_CONFIG_H
#define FREERTOS_IP_CONFIG_H

/* Basic configuration for TCP/IP stack */
#define ipconfigUSE_TCP                        1
#define ipconfigUSE_UDP                        1
#define ipconfigUSE_DNS                        0
#define ipconfigUSE_DHCP                       0

/* Network configuration */
#define ipconfigIP_ADDR0                       192
#define ipconfigIP_ADDR1                       168
#define ipconfigIP_ADDR2                       1
#define ipconfigIP_ADDR3                       95

#define ipconfigNET_MASK0                      255
#define ipconfigNET_MASK1                      255
#define ipconfigNET_MASK2                      255
#define ipconfigNET_MASK3                      0

#define ipconfigGATEWAY_ADDR0                  192
#define ipconfigGATEWAY_ADDR1                  168
#define ipconfigGATEWAY_ADDR2                  1
#define ipconfigGATEWAY_ADDR3                  1

/* TCP/IP stack configuration */
#define ipconfigTCP_MSS                        536
#define ipconfigTCP_TX_BUFFER_LENGTH           1024
#define ipconfigTCP_RX_BUFFER_LENGTH           1024
#define ipconfigMAXIMUM_DISCOVER_TX_PERIOD     ( pdMS_TO_TICKS( 30000U ) )

/* Driver configuration */
#define ipconfigDRIVER_INCLUDED_TX_IP_CHECKSUM 1
#define ipconfigDRIVER_INCLUDED_RX_IP_CHECKSUM 1
#define ipconfigZERO_COPY_RX_DRIVER           1
#define ipconfigZERO_COPY_TX_DRIVER           1

/* Buffer and queue sizes */
#define ipconfigNUM_NETWORK_BUFFER_DESCRIPTORS 5
#define ipconfigEVENT_QUEUE_LENGTH            ( ipconfigNUM_NETWORK_BUFFER_DESCRIPTORS + 5 )

/* Include FreeRTOS+TCP trace macros */
#define ipconfigHAS_PRINTF                     0
#define ipconfigHAS_DEBUG_PRINTF              0

#endif /* FREERTOS_IP_CONFIG_H */
