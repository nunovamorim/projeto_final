cmake_minimum_required(VERSION 3.10)
project(SatelliteSimulation C ASM)

# This needs to be at the very beginning of the CMakeLists.txt file
cmake_minimum_required(VERSION 3.10)

# Set cross-compilation
set(CMAKE_SYSTEM_NAME Generic)
set(CMAKE_SYSTEM_PROCESSOR ARM)
set(CMAKE_TRY_COMPILE_TARGET_TYPE STATIC_LIBRARY)

project(SatelliteSimulation C ASM)

# Set build type
set(CMAKE_BUILD_TYPE Debug)

# FreeRTOS source directory - adjust this path as needed
set(FREERTOS_DIR ${CMAKE_SOURCE_DIR}/FreeRTOS)

# Add FreeRTOS source files
set(FREERTOS_SOURCES
    ${FREERTOS_DIR}/FreeRTOS/Source/tasks.c
    ${FREERTOS_DIR}/FreeRTOS/Source/queue.c
    ${FREERTOS_DIR}/FreeRTOS/Source/list.c
    ${FREERTOS_DIR}/FreeRTOS/Source/timers.c
    ${FREERTOS_DIR}/FreeRTOS/Source/event_groups.c
    ${FREERTOS_DIR}/FreeRTOS/Source/stream_buffer.c
    ${FREERTOS_DIR}/FreeRTOS/Source/portable/MemMang/heap_4.c
    ${FREERTOS_DIR}/FreeRTOS/Source/portable/GCC/ARM_CM3/port.c
)

# Network source files
set(NETWORK_SOURCES
    ${CMAKE_SOURCE_DIR}/comm/tcp_client.c
)

# Add startup and system files
set(SYSTEM_SOURCES
    ${CMAKE_SOURCE_DIR}/startup_stm32.s
)

# Add our source files
set(SATELLITE_SOURCES
    ${CMAKE_SOURCE_DIR}/main.c
    ${CMAKE_SOURCE_DIR}/tasks/main_so.c
    ${CMAKE_SOURCE_DIR}/tasks/tc_proc.c
    ${CMAKE_SOURCE_DIR}/tasks/adcs_proc.c
    ${CMAKE_SOURCE_DIR}/tasks/tm_proc.c
    ${CMAKE_SOURCE_DIR}/comm/tcp_client.c
    ${CMAKE_SOURCE_DIR}/src/utils.c
    ${CMAKE_SOURCE_DIR}/src/system_stm32f1xx.c
    ${CMAKE_SOURCE_DIR}/src/freertos_hooks.c
)

# Include directories
include_directories(
    ${CMAKE_SOURCE_DIR}/include
    ${FREERTOS_DIR}/FreeRTOS/Source/include
    ${FREERTOS_DIR}/FreeRTOS/Source/portable/GCC/ARM_CM3
)

# Compiler flags for ARM Cortex-M3
set(MCU_FLAGS "-mcpu=cortex-m3 -mthumb -mfloat-abi=soft")
set(COMMON_FLAGS "-ffunction-sections -fdata-sections -Wall -Wextra")
set(CMAKE_C_FLAGS "${MCU_FLAGS} ${COMMON_FLAGS} -DSTM32F103xB -DUSE_HAL_DRIVER")
set(CMAKE_ASM_FLAGS "${MCU_FLAGS}")
set(CMAKE_EXE_LINKER_FLAGS "${MCU_FLAGS} -specs=nano.specs -specs=nosys.specs -Wl,--gc-sections -Wl,-Map=${PROJECT_NAME}.map")

# Linker flags
set(CMAKE_EXE_LINKER_FLAGS "-mcpu=cortex-m3 -mthumb")
set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -mfloat-abi=soft")
set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -specs=nano.specs")
set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -Wl,--gc-sections")
set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -Wl,-Map=output.map")
set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -T${CMAKE_SOURCE_DIR}/stm32_flash.ld")

# Create executable
add_executable(satellite 
    ${FREERTOS_SOURCES}
    ${SYSTEM_SOURCES}
    ${SATELLITE_SOURCES}
    ${NETWORK_SOURCES}
)

# Set binary format
set_target_properties(satellite PROPERTIES
    SUFFIX ".elf"
)

# Generate binary files
add_custom_command(TARGET satellite POST_BUILD
    COMMAND ${CMAKE_OBJCOPY} -O ihex ${CMAKE_BINARY_DIR}/satellite.elf ${CMAKE_BINARY_DIR}/satellite.hex
    COMMAND ${CMAKE_OBJCOPY} -O binary ${CMAKE_BINARY_DIR}/satellite.elf ${CMAKE_BINARY_DIR}/satellite.bin
    COMMAND ${CMAKE_SIZE} ${CMAKE_BINARY_DIR}/satellite.elf
)

# Link libraries
target_link_libraries(satellite m) # Math library

# Add custom target for size information
add_custom_target(size ALL 
    COMMAND ${CMAKE_SIZE} ${CMAKE_BINARY_DIR}/satellite.elf
    DEPENDS satellite
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
)
