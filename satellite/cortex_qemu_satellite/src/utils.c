#include <stdio.h>

void vAssertCalled(const char* file, int line) {
    printf("Assert failed in %s, line %d\n", file, line);
    while(1) {
        /* Infinite loop to stop execution */
    }
}
