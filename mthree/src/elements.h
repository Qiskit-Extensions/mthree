/*
This code is part of Mthree.

(C) Copyright IBM 2024.

This code is licensed under the Apache License, Version 2.0. You may
obtain a copy of this license in the LICENSE.txt file in the root directory
of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.

Any modifications or derivative works of this code must retain this
copyright notice, and modified files need to carry a notice indicating
that they have been altered from the originals.
*/
#include <stddef.h>

#pragma once

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
