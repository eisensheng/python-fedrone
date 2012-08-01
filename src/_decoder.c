#include <string.h>
#include "idct8.h"
#include "uvlc-decoder.h"
#include "_decoder.h"


static PyObject *
__decode_uvlc_frame (
    PyObject *self,
    PyObject *args
)
{
    PyObject *input_buffer;

    if (!PyArg_ParseTuple(args, "S:decode_h263_uvlc", &input_buffer))
         return NULL;

    return FeDrone_uvlc_decode_frame(input_buffer);
}


static PyMethodDef __decoder_module_methods[] = {
    {"decode_uvlc_frame", __decode_uvlc_frame, METH_VARARGS,
     "Decode single UVLC frame"},

    {NULL, NULL, 0, NULL}
};


PyMODINIT_FUNC
init_decoder (void)
{
    Py_InitModule("_decoder", __decoder_module_methods);
}
