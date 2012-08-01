#include "idct8.h"


#define ONE ((int32_t)1)
#define FIX_0_298631336 ((int32_t)2446)
#define FIX_0_390180644 ((int32_t)3196)
#define FIX_0_541196100 ((int32_t)4433)
#define FIX_0_765366865 ((int32_t)6270)
#define FIX_0_899976223 ((int32_t)7373)
#define FIX_1_175875602 ((int32_t)9633)
#define FIX_1_501321110 ((int32_t)12299)
#define FIX_1_847759065 ((int32_t)15137)
#define FIX_1_961570560 ((int32_t)16069)
#define FIX_2_053119869 ((int32_t)16819)
#define FIX_2_562915447 ((int32_t)20995)
#define FIX_3_072711026 ((int32_t)25172)

#define CONST_BITS (13)
#define PASS1_BITS (1)

#define MULTIPLY(a, b) ((a) * (b))
#define RIGHT_SHIFT(x, shift) ((x) >> (shift))
#define DESCALE(x, n) \
    ({ __typeof__((x)) ___x = (x); \
       __typeof__((n)) ___n = (n); \
       RIGHT_SHIFT((___x) + (ONE << ((___n) - 1)), ___n); })


void
FeDrone_inverse_dct8 (
    int32_t *block
)
{
    int32_t  tmp0, tmp1, tmp2, tmp3,
             tmp10, tmp11, tmp12, tmp13,
             z1, z2, z3, z4, z5,
             workspace[DCT8_SIZE2];
    int32_t *ws_ptr = workspace;
    int32_t *out_ptr = block,
            *in_ptr = block,
             idx;

    for (idx = DCT8_SIZE; idx > 0; idx--, in_ptr++, ws_ptr++) {
        if (in_ptr[DCT8_SIZE * 1] == 0 && in_ptr[DCT8_SIZE * 2] == 0 &&
            in_ptr[DCT8_SIZE * 3] == 0 && in_ptr[DCT8_SIZE * 4] == 0 &&
            in_ptr[DCT8_SIZE * 5] == 0 && in_ptr[DCT8_SIZE * 6] == 0 &&
            in_ptr[DCT8_SIZE * 7] == 0)
        {
            int32_t dcval = in_ptr[DCT8_SIZE * 0] << PASS1_BITS;

            ws_ptr[DCT8_SIZE * 0] = dcval;
            ws_ptr[DCT8_SIZE * 1] = dcval;
            ws_ptr[DCT8_SIZE * 2] = dcval;
            ws_ptr[DCT8_SIZE * 3] = dcval;
            ws_ptr[DCT8_SIZE * 4] = dcval;
            ws_ptr[DCT8_SIZE * 5] = dcval;
            ws_ptr[DCT8_SIZE * 6] = dcval;
            ws_ptr[DCT8_SIZE * 7] = dcval;

            continue;
        }

        z2 = in_ptr[DCT8_SIZE * 2];
        z3 = in_ptr[DCT8_SIZE * 6];

        z1 = MULTIPLY(z2 + z3, FIX_0_541196100);
        tmp2 = z1 + MULTIPLY(z3, - FIX_1_847759065);
        tmp3 = z1 + MULTIPLY(z2, FIX_0_765366865);

        z2 = in_ptr[DCT8_SIZE * 0];
        z3 = in_ptr[DCT8_SIZE * 4];

        tmp0 = (z2 + z3) << CONST_BITS;
        tmp1 = (z2 - z3) << CONST_BITS;

        tmp10 = tmp0 + tmp3;
        tmp13 = tmp0 - tmp3;
        tmp11 = tmp1 + tmp2;
        tmp12 = tmp1 - tmp2;

        tmp0 = in_ptr[DCT8_SIZE * 7];
        tmp1 = in_ptr[DCT8_SIZE * 5];
        tmp2 = in_ptr[DCT8_SIZE * 3];
        tmp3 = in_ptr[DCT8_SIZE * 1];

        z1 = tmp0 + tmp3;
        z2 = tmp1 + tmp2;
        z3 = tmp0 + tmp2;
        z4 = tmp1 + tmp3;
        z5 = MULTIPLY(z3 + z4, FIX_1_175875602); 

        tmp0 = MULTIPLY(tmp0,  FIX_0_298631336);
        tmp1 = MULTIPLY(tmp1,  FIX_2_053119869);
        tmp2 = MULTIPLY(tmp2,  FIX_3_072711026);
        tmp3 = MULTIPLY(tmp3,  FIX_1_501321110);
        z1   = MULTIPLY(  z1, -FIX_0_899976223);
        z2   = MULTIPLY(  z2, -FIX_2_562915447);
        z3   = MULTIPLY(  z3, -FIX_1_961570560);
        z4   = MULTIPLY(  z4, -FIX_0_390180644);

        z3 += z5;
        z4 += z5;

        tmp0 += z1 + z3;
        tmp1 += z2 + z4;
        tmp2 += z2 + z3;
        tmp3 += z1 + z4;

        ws_ptr[DCT8_SIZE * 0] = DESCALE(tmp10 + tmp3, CONST_BITS - PASS1_BITS);
        ws_ptr[DCT8_SIZE * 7] = DESCALE(tmp10 - tmp3, CONST_BITS - PASS1_BITS);
        ws_ptr[DCT8_SIZE * 1] = DESCALE(tmp11 + tmp2, CONST_BITS - PASS1_BITS);
        ws_ptr[DCT8_SIZE * 6] = DESCALE(tmp11 - tmp2, CONST_BITS - PASS1_BITS);
        ws_ptr[DCT8_SIZE * 2] = DESCALE(tmp12 + tmp1, CONST_BITS - PASS1_BITS);
        ws_ptr[DCT8_SIZE * 5] = DESCALE(tmp12 - tmp1, CONST_BITS - PASS1_BITS);
        ws_ptr[DCT8_SIZE * 3] = DESCALE(tmp13 + tmp0, CONST_BITS - PASS1_BITS);
        ws_ptr[DCT8_SIZE * 4] = DESCALE(tmp13 - tmp0, CONST_BITS - PASS1_BITS);
    }

    for (ws_ptr = workspace, idx = 0; 
         idx < DCT8_SIZE; 
         idx++, ws_ptr += DCT8_SIZE, out_ptr += DCT8_SIZE) 
    {
        z2 = ws_ptr[2];
        z3 = ws_ptr[6];

        z1 = MULTIPLY(z2 + z3, FIX_0_541196100);
        tmp2 = z1 + MULTIPLY(z3, - FIX_1_847759065);
        tmp3 = z1 + MULTIPLY(z2, FIX_0_765366865);

        tmp0 = (ws_ptr[0] + ws_ptr[4]) << CONST_BITS;
        tmp1 = (ws_ptr[0] - ws_ptr[4]) << CONST_BITS;

        tmp10 = tmp0 + tmp3;
        tmp13 = tmp0 - tmp3;
        tmp11 = tmp1 + tmp2;
        tmp12 = tmp1 - tmp2;

        tmp0 = ws_ptr[7];
        tmp1 = ws_ptr[5];
        tmp2 = ws_ptr[3];
        tmp3 = ws_ptr[1];

        z1 = tmp0 + tmp3;
        z2 = tmp1 + tmp2;
        z3 = tmp0 + tmp2;
        z4 = tmp1 + tmp3;
        z5 = MULTIPLY(z3 + z4, FIX_1_175875602); 

        tmp0 = MULTIPLY(tmp0, FIX_0_298631336); 
        tmp1 = MULTIPLY(tmp1, FIX_2_053119869); 
        tmp2 = MULTIPLY(tmp2, FIX_3_072711026);
        tmp3 = MULTIPLY(tmp3, FIX_1_501321110); 
        z1 = MULTIPLY(z1, - FIX_0_899976223); 
        z2 = MULTIPLY(z2, - FIX_2_562915447); 
        z3 = MULTIPLY(z3, - FIX_1_961570560); 
        z4 = MULTIPLY(z4, - FIX_0_390180644);

        z3 += z5;
        z4 += z5;

        tmp0 += z1 + z3;
        tmp1 += z2 + z4;
        tmp2 += z2 + z3;
        tmp3 += z1 + z4;

        out_ptr[0] = (tmp10 + tmp3) >> (CONST_BITS + PASS1_BITS + 3);
        out_ptr[7] = (tmp10 - tmp3) >> (CONST_BITS + PASS1_BITS + 3);
        out_ptr[1] = (tmp11 + tmp2) >> (CONST_BITS + PASS1_BITS + 3);
        out_ptr[6] = (tmp11 - tmp2) >> (CONST_BITS + PASS1_BITS + 3);
        out_ptr[2] = (tmp12 + tmp1) >> (CONST_BITS + PASS1_BITS + 3);
        out_ptr[5] = (tmp12 - tmp1) >> (CONST_BITS + PASS1_BITS + 3);
        out_ptr[3] = (tmp13 + tmp0) >> (CONST_BITS + PASS1_BITS + 3);
        out_ptr[4] = (tmp13 - tmp0) >> (CONST_BITS + PASS1_BITS + 3);
    }
}
