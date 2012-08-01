#include <stdlib.h>
#include <stdio.h>
#include <stdarg.h>

#include <Python.h>

#include "bitstream.h"


typedef struct FeDrone_BitStreamReader_ {
    PyObject *data_buffer;
    uint32_t  offset;
} FeDrone_BitStreamReader;


static inline void
__BitStreamReader_seek_forward (
    FeDrone_BitStreamReader *self,
    uint32_t                 bits
)
{
    self->offset += bits;
}


static inline uint32_t
__BitStreamReader_peek (
    FeDrone_BitStreamReader *self,
    uint32_t                 bits
)
{
    uint32_t *data = (uint32_t *)PyString_AS_STRING(self->data_buffer);
    uint64_t  chunk = *(uint64_t *)(data + (self->offset >> 5));
    uint32_t  shift = (64 - bits) - (self->offset & 31);
    uint64_t  mask = ((1ull << bits) - 1) << shift;
    uint32_t  output;
    
    chunk = chunk << 32 | (chunk >> 32 & 0xffffffffull);
    output = (uint32_t)(((chunk & mask) >> shift) & ((1ull << bits) - 1));

    return output;
}


static inline uint32_t
__BitStreamReader_read (
    FeDrone_BitStreamReader *self,
    uint32_t                 bits
)
{
    uint32_t output = __BitStreamReader_peek(self, bits);

    __BitStreamReader_seek_forward(self, bits);

    return output;
}


static inline void
__BitStreamReader_read_n_va (
    FeDrone_BitStreamReader *self,
    uint32_t                *out_var,
    va_list                  arg_list
)
{
    while (out_var != NULL) {
        uint32_t bits = va_arg(arg_list, uint32_t);

        *out_var = __BitStreamReader_read(self, bits);

        out_var = va_arg(arg_list, uint32_t *);
    }
}


static inline void
__BitStreamReader_align (
    FeDrone_BitStreamReader *self
)
{
    __BitStreamReader_seek_forward(self, (8 - (self->offset & 7)) & 7);
}


FeDrone_BitStreamReader *
FeDrone_BitStreamReader_new (
    PyObject *data_buffer
)
{
    FeDrone_BitStreamReader *new_reader;

    new_reader = PyMem_NEW(FeDrone_BitStreamReader, 1);

    new_reader->data_buffer = (Py_INCREF(data_buffer), data_buffer);
    new_reader->offset = 0;

    return new_reader;
}


void
FeDrone_BitStreamReader_free (
    FeDrone_BitStreamReader *self
)
{
    Py_DECREF(self->data_buffer);
    self->data_buffer = NULL;

    PyMem_FREE(self);
}


uint32_t
FeDrone_BitStreamReader_peek (
    FeDrone_BitStreamReader *self,
    uint32_t                 bits
)
{
    return __BitStreamReader_peek(self, bits);
}


uint32_t
FeDrone_BitStreamReader_read (
    FeDrone_BitStreamReader *self,
    uint32_t                 bits
)
{
    return __BitStreamReader_read(self, bits);
}


void
FeDrone_BitStreamReader_read_n (
    FeDrone_BitStreamReader *self,
    uint32_t                *out_var,
    ...
)
{
    va_list arg_list;

    va_start(arg_list, out_var);
    __BitStreamReader_read_n_va(self, out_var, arg_list);
    va_end(arg_list);
}


void
FeDrone_BitStreamReader_aligned_read_n (
    FeDrone_BitStreamReader *self,
    uint32_t                *out_var,
    ...
)
{
    va_list arg_list;

    __BitStreamReader_align(self);

    va_start(arg_list, out_var);
    __BitStreamReader_read_n_va(self, out_var, arg_list);
    va_end(arg_list);
}


void
FeDrone_BitStreamReader_align (
    FeDrone_BitStreamReader *self
)
{
    __BitStreamReader_align(self);
}


void
FeDrone_BitStreamReader_seek_forward (
    FeDrone_BitStreamReader *self,
    uint32_t                 bits
)
{
    return __BitStreamReader_seek_forward(self, bits);
}
