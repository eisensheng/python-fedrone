#ifndef __FEDRONE_UVLC_DECODER_H__
#define __FEDRONE_UVLC_DECODER_H__

#include <stdint.h>
#include <stdbool.h>

#include <Python.h>

#include "utils.h"


FE_INTERNAL
PyObject *
FeDrone_uvlc_decode_frame (
    PyObject *input_buffer
);


#endif
