# Toolchain file for ARM cross-compilation

# System
set(CMAKE_SYSTEM_NAME Generic)
set(CMAKE_SYSTEM_PROCESSOR ARM)

# Find the toolchain root directory
execute_process(
  COMMAND which arm-none-eabi-gcc
  OUTPUT_VARIABLE TOOLCHAIN_GCC
  OUTPUT_STRIP_TRAILING_WHITESPACE
)
get_filename_component(TOOLCHAIN_DIR ${TOOLCHAIN_GCC} DIRECTORY)

# The GNU tools for ARM
set(CMAKE_C_COMPILER ${TOOLCHAIN_DIR}/arm-none-eabi-gcc)
set(CMAKE_ASM_COMPILER ${TOOLCHAIN_DIR}/arm-none-eabi-gcc)
set(CMAKE_AR ${TOOLCHAIN_DIR}/arm-none-eabi-ar)
set(CMAKE_OBJCOPY ${TOOLCHAIN_DIR}/arm-none-eabi-objcopy)
set(CMAKE_OBJDUMP ${TOOLCHAIN_DIR}/arm-none-eabi-objdump)
set(CMAKE_SIZE ${TOOLCHAIN_DIR}/arm-none-eabi-size)

# Skip compiler test for cross-compilation
set(CMAKE_C_COMPILER_WORKS 1)
set(CMAKE_CXX_COMPILER_WORKS 1)
set(CMAKE_TRY_COMPILE_TARGET_TYPE STATIC_LIBRARY)

set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE ONLY)

# Compiler flags
set(CPU "-mcpu=cortex-m3")
set(FPU "-mfloat-abi=soft")
set(COMMON_FLAGS "${CPU} ${FPU} -mthumb -ffunction-sections -fdata-sections -Wall")

set(CMAKE_C_FLAGS_INIT "${COMMON_FLAGS}")
set(CMAKE_ASM_FLAGS_INIT "${COMMON_FLAGS}")
set(CMAKE_EXE_LINKER_FLAGS_INIT "${COMMON_FLAGS} -specs=nano.specs -Wl,--gc-sections")
