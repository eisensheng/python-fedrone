#ifndef __FEDRONE_UTILS_H__
#define __FEDRONE_UTILS_H__


#define MIN(x, y)  \
    ({ __typeof__ (x) ___x = (x); \
       __typeof__ (y) ___y = (y); \
       ___x < ___y ? ___x : ___y; })

#define MAX(x, y)  \
    ({ __typeof__ (x) ___x = (x); \
       __typeof__ (y) ___y = (y); \
       ___x > ___y ? ___x : ___y; })

#define FE_CLAMP(x, y, z)  \
    ({ __typeof__ (x) ___x = (x);          \
       __typeof__ (y) ___y = (y);          \
       __typeof__ (z) ___z = (z);          \
       ___x > ___z ? ___z : (___x < ___y ? ___y : ___x); })

#ifdef __GNUC__
#   define FE_LIKELY(x)    __builtin_expect((x), 1)
#   define FE_UNLIKELY(x)  __builtin_expect((x), 0)
#   define FE_INTERNAL     __attribute__((visibility("hidden")))
#else
#   define FE_LIKELY(x)    (x)
#   define FE_UNLIKELY(x)  (x)
#   define FE_INTERNAL
#endif


#endif
