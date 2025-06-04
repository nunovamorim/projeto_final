#include <errno.h>
#include <sys/stat.h>
#include <sys/times.h>
#include <sys/unistd.h>

// System initialization function
void SystemInit(void)
{
    // Basic system initialization
    // This would normally configure clocks, but we'll keep it simple for QEMU
}

// System calls required by newlib
void _exit(int status)
{
    (void)status;
    while(1) {}
}

int _close(int file)
{
    (void)file;
    return -1;
}

int _fstat(int file, struct stat *st)
{
    (void)file;
    st->st_mode = S_IFCHR;
    return 0;
}

int _isatty(int file)
{
    (void)file;
    return 1;
}

int _lseek(int file, int ptr, int dir)
{
    (void)file;
    (void)ptr;
    (void)dir;
    return 0;
}

int _read(int file, char *ptr, int len)
{
    (void)file;
    (void)ptr;
    (void)len;
    return 0;
}

int _write(int file, char *ptr, int len)
{
    (void)file;
    (void)ptr;
    return len;
}

int _getpid(void)
{
    return 1;
}

int _kill(int pid, int sig)
{
    (void)pid;
    (void)sig;
    errno = EINVAL;
    return -1;
}

void *_sbrk(int incr)
{
    extern char _end;
    static char *heap_end = &_end;
    char *prev_heap_end;

    prev_heap_end = heap_end;
    heap_end += incr;

    return (void *)prev_heap_end;
}
