/* Copyright (c) 2024 mthree */
#include <stddef.h>

static inline float compute_element(unsigned int row,
                                   unsigned int col,
                                   const unsigned char * __restrict bitstrings,
                                   const float * __restrict cals,
                                   unsigned int num_bits)
  {
    float res = 1.0F;
    size_t kk;
    unsigned int offset;
    const unsigned char * row_pos = &bitstrings[num_bits*row];
    const unsigned char * col_pos = &bitstrings[num_bits*col];
    #pragma omp simd reduction(*:res)
    for (kk=0; kk < num_bits; ++kk)
    {
      offset = 2*row_pos[kk] + col_pos[kk];
      res *= cals[4*kk+offset];
    }
    return res;
  }
