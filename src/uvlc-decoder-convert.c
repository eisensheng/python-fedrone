#include "utils.h"
#include "uvlc-decoder.h"
#include "uvlc-decoder-priv.h"


static const uint32_t __mb_to_gob_map[] = {
      0,   1,   2,   3,   4,   5,   6,   7,
     16,  17,  18,  19,  20,  21,  22,  23,
     32,  33,  34,  35,  36,  37,  38,  39,
     48,  49,  50,  51,  52,  53,  54,  55,
     64,  65,  66,  67,  68,  69,  70,  71,
     80,  81,  82,  83,  84,  85,  86,  87,
     96,  97,  98,  99, 100, 101, 102, 103,
    112, 113, 114, 115, 116, 117, 118, 119,
      8,   9,  10,  11,  12,  13,  14,  15,
     24,  25,  26,  27,  28,  29,  30,  31,
     40,  41,  42,  43,  44,  45,  46,  47,
     56,  57,  58,  59,  60,  61,  62,  63,
     72,  73,  74,  75,  76,  77,  78,  79,
     88,  89,  90,  91,  92,  93,  94,  95,
    104, 105, 106, 107, 108, 109, 110, 111,
    120, 121, 122, 123, 124, 125, 126, 127,
    128, 129, 130, 131, 132, 133, 134, 135,
    144, 145, 146, 147, 148, 149, 150, 151,
    160, 161, 162, 163, 164, 165, 166, 167,
    176, 177, 178, 179, 180, 181, 182, 183,
    192, 193, 194, 195, 196, 197, 198, 199,
    208, 209, 210, 211, 212, 213, 214, 215,
    224, 225, 226, 227, 228, 229, 230, 231,
    240, 241, 242, 243, 244, 245, 246, 247,
    136, 137, 138, 139, 140, 141, 142, 143,
    152, 153, 154, 155, 156, 157, 158, 159,
    168, 169, 170, 171, 172, 173, 174, 175,
    184, 185, 186, 187, 188, 189, 190, 191,
    200, 201, 202, 203, 204, 205, 206, 207,
    216, 217, 218, 219, 220, 221, 222, 223,
    232, 233, 234, 235, 236, 237, 238, 239,
    248, 249, 250, 251, 252, 253, 254, 255
};

static const uint32_t __scale_table[]  = {
     0,  0,  1,  1,  2,  2,  3,  3,
     0,  0,  1,  1,  2,  2,  3,  3,
     8,  8,  9,  9, 10, 10, 11, 11,
     8,  8,  9,  9, 10, 10, 11, 11,
    16, 16, 17, 17, 18, 18, 19, 19,
    16, 16, 17, 17, 18, 18, 19, 19,
    24, 24, 25, 25, 26, 26, 27, 27,
    24, 24, 25, 25, 26, 26, 27, 27,
     4,  4,  5,  5,  6,  6,  7,  7,
     4,  4,  5,  5,  6,  6,  7,  7,
    12, 12, 13, 13, 14, 14, 15, 15,
    12, 12, 13, 13, 14, 14, 15, 15,
    20, 20, 21, 21, 22, 22, 23, 23,
    20, 20, 21, 21, 22, 22, 23, 23,
    28, 28, 29, 29, 30, 30, 31, 31,
    28, 28, 29, 29, 30, 30, 31, 31,
    32, 32, 33, 33, 34, 34, 35, 35,
    32, 32, 33, 33, 34, 34, 35, 35,
    40, 40, 41, 41, 42, 42, 43, 43,
    40, 40, 41, 41, 42, 42, 43, 43,
    48, 48, 49, 49, 50, 50, 51, 51,
    48, 48, 49, 49, 50, 50, 51, 51,
    56, 56, 57, 57, 58, 58, 59, 59,
    56, 56, 57, 57, 58, 58, 59, 59,
    36, 36, 37, 37, 38, 38, 39, 39,
    36, 36, 37, 37, 38, 38, 39, 39,
    44, 44, 45, 45, 46, 46, 47, 47,
    44, 44, 45, 45, 46, 46, 47, 47,
    52, 52, 53, 53, 54, 54, 55, 55,
    52, 52, 53, 53, 54, 54, 55, 55,
    60, 60, 61, 61, 62, 62, 63, 63,
    60, 60, 61, 61, 62, 62, 63, 63
};


void
_DecoderState_store_ycbcr_as_rgb888x (
    __DecoderState *dec_state
)
{
    int32_t pos, j, y, cb, cr, r, g, b;

    for (uint32_t idx = 0; idx < 256; idx++) {
        pos = (__mb_to_gob_map[idx] & 15) + (__mb_to_gob_map[idx] >> 4)
                                          * dec_state->pic_header.width
                                          + dec_state->out_picture_offset;

        j = __scale_table[idx];
        y = dec_state->y_buf[idx] - 16;
        cb = dec_state->cb_buf[j] - 128;
        cr = dec_state->cr_buf[j] - 128;

        r = (298 * y            + 409 * cr + 128) >> 8;
        g = (298 * y - 100 * cb - 208 * cr + 128) >> 8;
        b = (298 * y + 516 * cb            + 128) >> 8;

        r = FE_CLAMP(r, 0x00, 0xff);
        g = FE_CLAMP(g, 0x00, 0xff);
        b = FE_CLAMP(b, 0x00, 0xff);

        dec_state->out_picture_buf[pos] = 0xff000000 | b << 16 | g << 8 | r;
    }
}
