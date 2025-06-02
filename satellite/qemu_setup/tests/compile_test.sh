#!/bin/bash

echo "Compilando teste POSIX..."
gcc -o test_posix_support test_posix_support.c -pthread -D_POSIX_C_SOURCE=200809L

if [ $? -eq 0 ]; then
    echo "Compilação bem sucedida. Executando teste..."
    ./test_posix_support
else
    echo "Erro na compilação!"
    exit 1
fi
