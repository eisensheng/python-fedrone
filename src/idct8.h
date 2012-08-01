#ifndef __FEDRONE_IDCT8_H__
#define __FEDRONE_IDCT8_H__

#include <stdint.h>

#include "utils.h"


#define DCT8_SIZE    8
#define DCT8_SIZE2  64


FE_INTERNAL
void
FeDrone_inverse_dct8 (
    int32_t *block
);

#endif
