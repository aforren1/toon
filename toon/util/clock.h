#include <stdint.h>
// based off https://github.com/floooh/sokol/blob/master/sokol_time.h

// https://github.com/floooh/sokol/blob/master/sokol_time.h#L193
#if defined(_WIN32) || (defined(__APPLE__) && defined(__MACH__))
int64_t int64_muldiv(int64_t value, int64_t numer, int64_t denom)
{
    int64_t q = value / denom;
    int64_t r = value % denom;
    return q * numer + r * numer / denom;
}
#endif

#if defined(_WIN32)
#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif
#include <windows.h>
typedef struct
{
    LARGE_INTEGER freq;
    LARGE_INTEGER start;
} _time_state_t;

void init_clock(_time_state_t *reference)
{
    QueryPerformanceFrequency(&reference->freq);
    QueryPerformanceCounter(&reference->start);
}

uint64_t clock_now(_time_state_t *reference)
{
    LARGE_INTEGER current_ticks;
    QueryPerformanceCounter(&current_ticks);
    return int64_muldiv(current_ticks.QuadPart - reference->start.QuadPart,
                        1000000000, reference->freq.QuadPart);
}

void set_ref(_time_state_t *reference, uint64_t value)
{
    reference->start.QuadPart = value;
}
uint64_t get_ref(_time_state_t *reference)
{
    return reference->start.QuadPart;
}

#elif defined(__APPLE__) && defined(__MACH__)
#include <mach/mach_time.h>
typedef struct
{
    mach_timebase_info_data_t timebase;
    uint64_t start;
} _time_state_t;

void init_clock(_time_state_t *reference)
{
    mach_timebase_info(&reference->timebase);
    reference->start = mach_absolute_time();
}

uint64_t clock_now(_time_state_t *reference)
{
    const uint64_t current_time = mach_absolute_time() - reference->start;
    return int64_muldiv(current_time, reference->timebase.numer, reference->timebase.denom);
}

void set_ref(_time_state_t *reference, uint64_t value)
{
    reference->start = value;
}
uint64_t get_ref(_time_state_t *reference)
{
    return reference->start;
}
#else // Linux
#include <time.h>
typedef struct
{
    uint64_t start;
} _time_state_t;

uint64_t linux_now(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000000000 + (uint64_t)ts.tv_nsec;
}
void init_clock(_time_state_t *reference)
{
    reference->start = linux_now();
}

uint64_t clock_now(_time_state_t *reference)
{
    return linux_now() - reference->start;
}
void set_ref(_time_state_t *reference, uint64_t value)
{
    reference->start = value;
}
uint64_t get_ref(_time_state_t *reference)
{
    return reference->start;
}
#endif
