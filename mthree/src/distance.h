/* Copyright (c) 2024 mthree */
#include <stddef.h>
#include <stdbool.h>


static inline bool within_distance(unsigned int row,
                                   unsigned int col,
                                   const unsigned char * __restrict bitstrings,
                                   unsigned int num_bits,
                                   unsigned int distance)
  /**
   * @brief Computes if two bit-strings are within the specified Hamming distance.
   *
   * @param row Index for row bit-string
   * @param col Index for col bit-string
   * @param bitstrings Pointer to array of bit-strings
   * @param num_bits Number of bits in a single bit-string
   * @param distance Max Hamming distance
   *
   * @return Are the bit-strings within the Hamming distance 
   */
  {
    size_t kk;
    unsigned int sum=0;
    const unsigned char * row_pos = &bitstrings[num_bits*row];
    const unsigned char * col_pos = &bitstrings[num_bits*col];
    #pragma omp simd reduction(+:sum)
    for (kk = 0; kk < num_bits; ++kk)
        {
          sum += row_pos[kk] ^ col_pos[kk];
        }
    return sum <= distance;
    
  }


static inline unsigned int binomial_coeff(unsigned int n, unsigned int k)
  {
    if (k > n)
      {
        return 0U;
      }
    else if ((k == 0) || (k == n))
      {
        return 1U;
      }
    else if ((k == 1) || (k == (n-1)))
      {
        return n;
      }
    else if (k+k < n)
      {
        return (binomial_coeff(n-1, k-1) * n) / k;
      }
    else
      {
        return (binomial_coeff(n-1, k) * n) / (n-k);
      }
  }


unsigned int hamming_terms(unsigned int num_bits, unsigned int distance)
{
  unsigned int kk, out = 0;
  for (kk=0; kk < (distance+1); ++kk)
    {
      out += binomial_coeff(num_bits, kk);
    }
  return out;
}
