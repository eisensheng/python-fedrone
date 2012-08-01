#ifndef __FEDRONE_UVLC_DECODER_PRIV_H__
#define __FEDRONE_UVLC_DECODER_PRIV_H__

#include "utils.h"
#include "idct8.h"
#include "bitstream.h"


typedef struct __PictureHeader_ {
    uint32_t width;
    uint32_t height;
    uint32_t type;
    uint32_t quant;
    uint32_t frame_nr;
} __PictureHeader;


typedef struct __DecoderState_ {
    FeDrone_BitStreamReader *bitstream;

    __PictureHeader          pic_header;

    int32_t                  y_buf[DCT8_SIZE2 * 4],
                             cb_buf[DCT8_SIZE2],
                             cr_buf[DCT8_SIZE2];

    uint32_t                 blocks,
                             slices,
                             slice,
                             block,
                             out_picture_offset;

    size_t                   out_picture_len;
    uint32_t                *out_picture_buf;
} __DecoderState;


FE_INTERNAL
void
_DecoderState_store_ycbcr_as_rgb888x (
    __DecoderState *decoder_state
);


#endif
