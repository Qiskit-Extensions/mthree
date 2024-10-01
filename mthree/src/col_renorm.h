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
#include "elements.h"

#pragma once

void compute_col_norms(float * col_norms,
                       const unsigned char * __restrict bitstrings,
                       const float * __restrict cals,
                       unsigned int num_bits,
                       unsigned int num_elems,
                       unsigned int distance)
    /**
   * @brief Computes the renormalization factor for each column of A-matrix
   *
   * @param col_norms Pointer to where to store col norm data
   * @param bitstrings Pointer to array of bitstrings
   * @param cals Pointer to array containing calibration data
   * @param num_bits Number of bits in a single bit-string
   * @param num_elems Number of elements (dimension) of reduced A-matrix
   * @param distance Max Hamming distance
   */
    {

      size_t col;
      bool MAX_DIST = false;
      int num_terms = -1;

      if (distance == num_bits)
      {
        MAX_DIST = true;
      }
      else{
        num_terms = (int)hamming_terms(num_bits, distance, num_elems); 
      }

      #pragma omp parallel for
      for (col = 0; col < num_elems; ++col)
      {
        float col_norm = 0.0F;
        size_t row;
        int terms = 0;
        for (row = 0; row < num_elems; ++row)
        {
          if (MAX_DIST || within_distance(row, col, bitstrings, num_bits, distance))
          {
            col_norm += compute_element(row, col, bitstrings, cals, num_bits);
            terms += 1;
            if (terms == num_terms)
            {
              break;
            }
          }
        }
        col_norms[col] = col_norm;
      }

    }
