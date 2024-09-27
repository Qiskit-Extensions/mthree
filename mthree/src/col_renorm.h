/* Copyright (c) 2024 mthree */
#include <stddef.h>
#include <stdbool.h>
#include "distance.h"
#include "elements.h"


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
        num_terms = hamming_terms(num_bits, distance); 
      }

      #pragma omp parallel for
      for (col = 0; col < num_elems; ++col)
      {
        bool flag = false;
        float col_norm = 0.0F;
        size_t row;
        int terms = 0;
        for (row = 0; row < num_elems; ++row)
        {
          if (flag) continue;
          if (MAX_DIST || within_distance(row, col, bitstrings, num_bits, distance))
          {
            col_norm += compute_element(row, col, bitstrings, cals, num_bits);
            terms += 1;
            if (terms == num_terms)
            {
              flag = true;
            }
          }
        }
        col_norms[col] = col_norm;
      }

    }
