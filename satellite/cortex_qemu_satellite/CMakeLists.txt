cmake_minimum_required(VERSION 3.10)
project(SatelliteSimulation C ASM)

# FreeRTOS source directory - adjust this path as needed
set(FREERTOS_DIR ${CMAKE_SOURCE_DIR}/FreeRTOS)

# Add FreeRTOS source files
set(FREERTOS_SOURCES
    ${FREERTOS_DIR}/Source/tasks.c
    ${FREERTOS_DIR}/Source/queue.c
    ${FREERTOS_DIR}/Source/list.c
    ${FREERTOS_DIR}/Source/timers.c
    ${FREERTOS_DIR}/Source/portable/MemMang/heap_4.c
    ${FREERTOS_DIR}/Source/portable/GCC/ARM_CM3/port.c
)

# Add startup and system files
set(SYSTEM_SOURCES
    ${CMAKE_SOURCE_DIR}/cortex_qemu_satellite/startup_stm32.s
)

# Add our source files
set(SATELLITE_SOURCES
    ${CMAKE_SOURCE_DIR}/cortex_qemu_satellite/main.c
    ${CMAKE_SOURCE_DIR}/cortex_qemu_satellite/tasks/main_so.c
    ${CMAKE_SOURCE_DIR}/cortex_qemu_satellite/tasks/tc_proc.c
    ${CMAKE_SOURCE_DIR}/cortex_qemu_satellite/tasks/adcs_proc.c
    ${CMAKE_SOURCE_DIR}/cortex_qemu_satellite/tasks/tm_proc.c
    ${CMAKE_SOURCE_DIR}/cortex_qemu_satellite/comm/tcp_client.c
)

# Include directories
include_directories(
    ${CMAKE_SOURCE_DIR}/cortex_qemu_satellite/include
    ${FREERTOS_DIR}/Source/include
    ${FREERTOS_DIR}/Source/portable/GCC/ARM_CM3
)

# Compiler flags
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -mcpu=cortex-m3 -mthumb -mfloat-abi=soft -Wall -O2")
set(CMAKE_ASM_FLAGS "${CMAKE_ASM_FLAGS} -mcpu=cortex-m3 -mthumb -mfloat-abi=soft")

# Linker flags
set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -T${CMAKE_SOURCE_DIR}/cortex_qemu_satellite/stm32_flash.ld -mcpu=cortex-m3 -mthumb -mfloat-abi=soft --specs=nosys.specs -Wl,--gc-sections")

# Create executable
add_executable(satellite ${FREERTOS_SOURCES} ${SYSTEM_SOURCES} ${SATELLITE_SOURCES})

# Set binary format
set_target_properties(satellite PROPERTIES
    SUFFIX ".elf"
)

# Generate binary file
add_custom_command(TARGET satellite POST_BUILD
    COMMAND ${CMAKE_OBJCOPY} -O binary satellite.elf satellite.bin
)

# Link libraries
target_link_libraries(satellite m) # Math library
