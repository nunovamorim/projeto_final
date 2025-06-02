#include <stdio.h>
#include <pthread.h>
#include <unistd.h>
#include <time.h>
#include <errno.h>
#include <semaphore.h>
#include <stdlib.h>

void* dummy_thread(void* arg) {
    printf("Thread POSIX executando...\n");
    return NULL;
}

int main() {
    printf("Iniciando testes de suporte POSIX...\n\n");
    
    // 1. Teste de threads POSIX
    pthread_t thread;
    if (pthread_create(&thread, NULL, dummy_thread, NULL) == 0) {
        printf("✓ Suporte a threads POSIX: OK\n");
        pthread_join(thread, NULL);
    } else {
        printf("✗ Falha no suporte a threads POSIX\n");
        return 1;
    }
    
    // 2. Teste de temporizadores POSIX
    struct timespec ts;
    if (clock_gettime(CLOCK_REALTIME, &ts) == 0) {
        printf("✓ Suporte a temporizadores POSIX: OK\n");
    } else {
        printf("✗ Falha no suporte a temporizadores POSIX\n");
        return 1;
    }
    
    // 3. Teste de semáforos POSIX
    sem_t semaphore;
    if (sem_init(&semaphore, 0, 1) == 0) {
        printf("✓ Suporte a semáforos POSIX: OK\n");
        sem_destroy(&semaphore);
    } else {
        printf("✗ Falha no suporte a semáforos POSIX\n");
        return 1;
    }

    printf("\nTodos os testes POSIX concluídos com sucesso!\n");
    return 0;
}