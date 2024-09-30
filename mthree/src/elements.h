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
#include <stdbool.h>
#include "distance.h"

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


void column_elements(const unsigned char * __restrict bitstrings,
                     const float * __restrict cals_ptr,
                     unsigned int num_elems,
                     unsigned int num_bits,
                     unsigned int distance,
                     float * W_ptr,
                     float *  col_norms_ptr,
                     int num_terms,
                     bool MAX_DIST)
    {
      size_t jj;

      #pragma omp parallel for
      for (jj = 0; jj < num_elems; ++jj)
      {
        float temp, col_norm = 0;
        size_t ii;
        int terms = 0;
        float * col_ptr = &W_ptr[jj*num_elems];
        for (ii = 0; ii < num_elems; ++ii)
        {
          if (MAX_DIST || within_distance(ii, jj, bitstrings, num_bits, distance))
          {
            temp = compute_element(ii, jj, bitstrings, cals_ptr, num_bits);
            col_ptr[ii] = temp;
            col_norm += temp;
            terms += 1;
            if (terms == num_terms)
            {
              break;
            }
          }
        }
        col_norms_ptr[jj] = col_norm;
        #pragma omp simd
        for (ii = 0; ii < num_elems; ++ii)
          col_ptr[ii] /= col_norm;
      }
    }