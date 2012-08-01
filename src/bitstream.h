#ifndef __FEDRONE_BITSTREAM_H__
#define __FEDRONE_BITSTREAM_H__

#include <stdint.h>

#include "utils.h"


typedef struct FeDrone_BitStreamReader_ FeDrone_BitStreamReader;


FE_INTERNAL
FeDrone_BitStreamReader *
FeDrone_BitStreamReader_new (
    PyObject *data_buffer
);

FE_INTERNAL
void
FeDrone_BitStreamReader_free (
    FeDrone_BitStreamReader *self
);

FE_INTERNAL
uint32_t
FeDrone_BitStreamReader_peek (
    FeDrone_BitStreamReader *self,
    uint32_t                 bits
);

FE_INTERNAL
uint32_t
FeDrone_BitStreamReader_read (
    FeDrone_BitStreamReader *self,
    uint32_t                 bits
);

FE_INTERNAL
void
FeDrone_BitStreamReader_read_n (
    FeDrone_BitStreamReader *self,
    uint32_t                *out_var,
    ...
);

FE_INTERNAL
void
FeDrone_BitStreamReader_aligned_read_n (
    FeDrone_BitStreamReader *self,
    uint32_t                *out_var,
    ...
);

FE_INTERNAL
void
FeDrone_BitStreamReader_align (
    FeDrone_BitStreamReader *self
);

FE_INTERNAL
void
FeDrone_BitStreamReader_seek_forward (
    FeDrone_BitStreamReader *self,
    uint32_t                 bits
);


#endif 
