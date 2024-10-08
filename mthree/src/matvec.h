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

void matvec(const float * __restrict x,
            float * out,
            const float * __restrict col_norms,
            const unsigned char * __restrict bitstrings,
            const float * __restrict cals,
            unsigned int num_bits,
            unsigned int num_elems,
            unsigned int distance,
            int num_terms,
            bool MAX_DIST)
    /**
   * @brief Action of reduced A-matrix on a vector
   *
   * @param x Pointer to input vector of data
   * @param out Pointer to zeroed output vector
   * @param col_norms Pointer to where to store col norm data
   * @param bitstrings Pointer to array of bitstrings
   * @param cals Pointer to array containing calibration data
   * @param num_bits Number of bits in a single bit-string
   * @param num_elems Number of elements (dimension) of reduced A-matrix
   * @param distance Max Hamming distance
   * @param num_terms Number of terms within hamming distance
   * @param MAX_DIST Is the distance maximum (equal to number of bits)
   */
    {

      size_t row;

      #pragma omp parallel for
      for (row = 0; row < num_elems; ++row)
      {
        float temp_elem, row_sum = 0;
        size_t col;
        int terms = 0;
        for (col = 0; col < num_elems; ++col)
        {
          if (MAX_DIST || within_distance(row, col, bitstrings, num_bits, distance))
          {
            temp_elem = compute_element(row, col, bitstrings, cals, num_bits);
            temp_elem /= col_norms[col];
            row_sum += temp_elem * x[col];
            terms += 1;
            if (terms == num_terms)
            {
              break; /* Break out of col for-loop*/
            }
          }
        }
        out[row] = row_sum;
      }
    }


void rmatvec(const float * __restrict x,
             float * out,
             const float * __restrict col_norms,
             const unsigned char * __restrict bitstrings,
             const float * __restrict cals,
             unsigned int num_bits,
             unsigned int num_elems,
             unsigned int distance,
             int num_terms,
             bool MAX_DIST)
    /**
   * @brief Action of adjoint of reduced A-matrix on a vector
   *
   * @param x Pointer to input vector of data
   * @param out Pointer to zeroed output vector
   * @param col_norms Pointer to where to store col norm data
   * @param bitstrings Pointer to array of bitstrings
   * @param cals Pointer to array containing calibration data
   * @param num_bits Number of bits in a single bit-string
   * @param num_elems Number of elements (dimension) of reduced A-matrix
   * @param distance Max Hamming distance
   * @param num_terms Number of terms within hamming distance
   * @param MAX_DIST Is the distance maximum (equal to number of bits)
   */
    {

      size_t col;

      #pragma omp parallel for
      for (col = 0; col < num_elems; ++col)
      {
        float temp_elem, row_sum = 0;
        size_t row;
        int terms = 0;
        for (row = 0; row < num_elems; ++row)
        {
          if (MAX_DIST || within_distance(row, col, bitstrings, num_bits, distance))
          {
            temp_elem = compute_element(row, col, bitstrings, cals, num_bits);
            temp_elem /= col_norms[col];
            row_sum += temp_elem * x[row];
            terms += 1;
            if (terms == num_terms)
            {
              break;
            }
          }
        }
        out[col] = row_sum;
      }
    }