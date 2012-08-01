#include <stdlib.h>
#include <string.h>

#include "idct8.h"
#include "uvlc-decoder.h"
#include "uvlc-decoder-priv.h"


static const uint32_t __zigzag_table[] = {
     0,  1,  8, 16,  9,  2,  3, 10,
    17, 24, 32, 25, 18, 11,  4,  5,
    12, 19, 26, 33, 40, 48, 41, 34,
    27, 20, 13,  6,  7, 14, 21, 28,
    35, 42, 49, 56, 57, 50, 43, 36,
    29, 22, 15, 23, 30, 37, 44, 51,
    58, 59, 52, 45, 38, 31, 39, 46,
    53, 60, 61, 54, 47, 55, 62, 63,
};


static const uint32_t __quant_table[] = {
     3,  5,  7,  9, 11, 13, 15, 17,
     5,  7,  9, 11, 13, 15, 17, 19,
     7,  9, 11, 13, 15, 17, 19, 21,
     9, 11, 13, 15, 17, 19, 21, 23,
    11, 13, 15, 17, 19, 21, 23, 25,
    13, 15, 17, 19, 21, 23, 25, 27,
    15, 17, 19, 21, 23, 25, 27, 29,
    17, 19, 21, 23, 25, 27, 29, 31
};


static inline uint32_t
__count_leading_zeros (
    uint32_t value
)
{
    return __builtin_clz(value);
}


static bool
__decompress_value (
    __DecoderState *dec_state,
    int32_t        *run,
    int32_t        *level
)
{
    uint32_t stream_code = 0,
             stream_length = 0;
    int32_t  r = 0,
             zeros,
             sign;
    bool     more_data = true;

    stream_code = FeDrone_BitStreamReader_peek(dec_state->bitstream, 32);

    zeros = __count_leading_zeros(stream_code);
    stream_code <<= zeros + 1;
    stream_length += zeros + 1;

    if (zeros > 1) {
        r = stream_code >> (32 - (zeros - 1));

        stream_code <<= (zeros - 1);
        stream_length += (zeros - 1);

        *run = r + (1 << (zeros - 1));

    } else
        *run = zeros;

    zeros = __count_leading_zeros(stream_code);
    stream_code <<= zeros + 1;
    stream_length += zeros + 1;

    if (zeros == 1) {
        *run = 0;
        *level = 0;
        more_data = false;

    } else {
        if (zeros == 0) {
            zeros = 1;
            r = 1;
        }

        stream_length += zeros;

        stream_code >>= (32 - zeros);
        sign = stream_code & 1;

        if (zeros != 0) {
            r = stream_code >> 1;
            r += 1 << (zeros - 1);
        }

        *level = sign ? -r : r;
    }

    FeDrone_BitStreamReader_seek_forward(dec_state->bitstream, stream_length);

    return more_data;
}


static void
__unpack_block (
    __DecoderState *dec_state,
    int32_t        *out_block,
    bool            has_coeff
)
{
    memset(out_block, 0x00, sizeof(int32_t) * DCT8_SIZE2);

    out_block[0] = FeDrone_BitStreamReader_read(dec_state->bitstream, 10);
    out_block[0] *= __quant_table[0];

    if (FE_LIKELY(has_coeff)) {
        const uint32_t *zigzag_table = __zigzag_table;
        int32_t         code = 0,
                        run = 0;

        while (FE_LIKELY(__decompress_value(dec_state, &run, &code))) {
            int32_t index = *(zigzag_table += run + 1);

            out_block[index] = code * __quant_table[index];
        }
    }

    FeDrone_inverse_dct8(out_block);
}


static bool
__unpack_mb (
    __DecoderState *dec_state
)
{
    uint32_t mbc, mbdesc;

    FeDrone_BitStreamReader_read_n(dec_state->bitstream,
                                   &mbc, 1,
                                   &mbdesc, 8,
                                   NULL);

    if (FE_UNLIKELY(mbc != 0)) {
        PyErr_SetString(PyExc_ValueError, "mbc != 0");
        return false;

    } else if (FE_UNLIKELY(!(mbdesc >> 7 & 1))) {
        PyErr_SetString(PyExc_ValueError, "bad mbdesc");
        return false;
    }

    /* silently discarding mbdiff if available */
    if (FE_UNLIKELY(mbdesc >> 6 & 1))
        FeDrone_BitStreamReader_seek_forward(dec_state->bitstream, 2);

    __unpack_block(dec_state, dec_state->y_buf, mbdesc & 1);
    __unpack_block(dec_state, dec_state->y_buf + DCT8_SIZE2,
                   mbdesc >> 1 & 1);
    __unpack_block(dec_state, dec_state->y_buf + DCT8_SIZE2 * 2,
                   mbdesc >> 2 & 1);
    __unpack_block(dec_state, dec_state->y_buf + DCT8_SIZE2 * 3,
                   mbdesc >> 3 & 1);

    __unpack_block(dec_state, dec_state->cb_buf, mbdesc >> 4 & 1);
    __unpack_block(dec_state, dec_state->cr_buf, mbdesc >> 5 & 1);

    _DecoderState_store_ycbcr_as_rgb888x(dec_state);

    return true;
}


static bool
__test_gob_start_code (
    __DecoderState *dec_state
)
{
    uint32_t start_code, block_line;

    FeDrone_BitStreamReader_aligned_read_n(dec_state->bitstream,
                                           &start_code, 22,
                                           NULL);

    block_line = start_code & 0x1f;
    start_code &= ~0x1f;

    if (FE_LIKELY((start_code == 0x20) && (block_line == dec_state->slice)))
        return true;

    PyErr_Format(PyExc_ValueError,
                 "Bad GOBSC, got start_code: 0x%x, block_line: 0x%x, "
                     "expected_block_line: 0x%x",
                 start_code, block_line, dec_state->slice);

    return false;
}


static bool
__unpack_gob_header (
    __DecoderState *dec_state
)
{
    if (FE_UNLIKELY(!__test_gob_start_code(dec_state)))
        return false;

    /* silently discard the quant field */
    FeDrone_BitStreamReader_read(dec_state->bitstream, 5);

    return true;
}


static bool
__unpack_gob (
    __DecoderState *dec_state
)
{
    dec_state->out_picture_offset = 16 * dec_state->slice
                                       * dec_state->pic_header.width;

    for (dec_state->block = 0;
         dec_state->block < dec_state->blocks;
         dec_state->block++)
    {
        if (FE_UNLIKELY(!__unpack_mb(dec_state)))
            return false;

        dec_state->out_picture_offset += 16;
    }

    return true;
}


static bool
__unpack_header (
    __DecoderState  *dec_state,
    __PictureHeader *pic_header
)
{
    uint32_t format, resolution;

    if (FE_UNLIKELY(!__test_gob_start_code(dec_state)))
        return false;

    FeDrone_BitStreamReader_read_n(dec_state->bitstream,
                                   &format, 2,
                                   &resolution, 3,
                                   &pic_header->type, 3,
                                   &pic_header->quant, 5,
                                   &pic_header->frame_nr, 32,
                                   NULL);

    switch (format) {
    case 1: pic_header->width = 88; pic_header->height = 72; break;
    case 2: pic_header->width = 160; pic_header->height = 120; break;
    default: pic_header->width = 0; pic_header->height = 0; break;
    }
    pic_header->width <<= resolution - 1;
    pic_header->height <<= resolution - 1;

    return true;
}


static bool
__decoder_initialize (
    __DecoderState  *dec_state
)
{
    __PictureHeader *pic_header = &dec_state->pic_header;
    size_t           pic_length;

    if (FE_UNLIKELY(!__unpack_header(dec_state, pic_header)))
        return false;

    pic_length = sizeof(uint32_t) * pic_header->width * pic_header->height;
    dec_state->out_picture_len = pic_length;
    dec_state->out_picture_buf = PyMem_MALLOC(pic_length);
    if (FE_UNLIKELY(!dec_state->out_picture_buf))
        return (PyErr_NoMemory(), false);

    dec_state->blocks = pic_header->width >> 4;
    dec_state->slices = pic_header->height >> 4;

    return true;
}


static bool
__decoder_read_frame (
    __DecoderState *dec_state
)
{
    dec_state->slice = 0;

    if (FE_UNLIKELY(!__decoder_initialize(dec_state)))
        return false;

    if (FE_UNLIKELY(!__unpack_gob(dec_state)))
        return false;

    while (++dec_state->slice < dec_state->slices) {
        if (FE_UNLIKELY(!__unpack_gob_header(dec_state)))
            return false;

        if (FE_UNLIKELY(!__unpack_gob(dec_state)))
            return false;
    }

    return true;
}


PyObject *
FeDrone_uvlc_decode_frame (
    PyObject *input_buffer
)
{
    __DecoderState  dec_state;
    PyObject       *picture_desc = NULL;

    dec_state.out_picture_buf = NULL;
    dec_state.bitstream = FeDrone_BitStreamReader_new(input_buffer);

    if (FE_LIKELY(__decoder_read_frame(&dec_state))) {
        picture_desc = Py_BuildValue("(IIIs#)",
                                     dec_state.pic_header.width,
                                     dec_state.pic_header.height,
                                     dec_state.pic_header.frame_nr,
                                     (char *)dec_state.out_picture_buf,
                                     (int)dec_state.out_picture_len);
    }

    PyMem_FREE(dec_state.out_picture_buf);
    dec_state.out_picture_buf = NULL;

    FeDrone_BitStreamReader_free(dec_state.bitstream);
    dec_state.bitstream = NULL;

    return picture_desc;
}
