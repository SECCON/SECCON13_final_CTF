#include <immintrin.h>
#include <stdio.h>
#include <stdlib.h>

typedef long long i64;

static inline __m256i _mm256_mullo_epi64_emul(__m256i a, __m256i b) {
  const __m256i mask32 = _mm256_set1_epi64x(0xffffffff);
  __m256i aLo = _mm256_and_si256(a, mask32);
  __m256i aHi = _mm256_srli_epi64(a, 32);
  __m256i bLo = _mm256_and_si256(b, mask32);
  __m256i bHi = _mm256_srli_epi64(b, 32);
  __m256i prodLo = _mm256_mul_epu32(aLo, bLo);
  __m256i cross1 = _mm256_mul_epu32(aLo, bHi);
  __m256i cross2 = _mm256_mul_epu32(aHi, bLo);
  __m256i cross  = _mm256_add_epi64(cross1, cross2);
  __m128i shift32 = _mm_cvtsi32_si128(32);
  __m256i crossShl32 = _mm256_sll_epi64(cross, shift32);
  __m256i prod = _mm256_add_epi64(prodLo, crossShl32);
  return prod;
}

static inline i64 hsum_epi64_avx2(__m256i v) {
  __m128i lo128 = _mm256_castsi256_si128(v);
  __m128i hi128 = _mm256_extracti128_si256(v, 1);
  __m128i sum128 = _mm_add_epi64(lo128, hi128);
  __m128i hi64 = _mm_unpackhi_epi64(sum128, sum128);
  __m128i final = _mm_add_epi64(sum128, hi64);
  return _mm_cvtsi128_si64(final);
}

void matmul_avx2_colmajor(const i64 *A, const i64 *Bcol, i64 *C, size_t N) {
  for (size_t i = 0; i < N; i++) {
    for (size_t j = 0; j < N; j++) {
      __m256i vsum = _mm256_setzero_si256();
      int k = 0;
      for (; k + 4 <= N; k += 4) {
        __m256i va = _mm256_loadu_si256((const __m256i *)&A[i*N + k]);
        __m256i vb = _mm256_loadu_si256((const __m256i *)&Bcol[j*N + k]);
        __m256i vmul = _mm256_mullo_epi64_emul(va, vb);
        vsum = _mm256_add_epi64(vsum, vmul);
      }
      i64 sum = hsum_epi64_avx2(vsum);
      for (; k < N; k++)
        sum += A[i*N + k] * Bcol[j*N + k];
      C[i*N + j] = sum;
    }
  }
}

void transpose(const i64 *A, i64 *B, size_t n) {
  for (size_t i = 0; i < n; i++) {
    for (size_t j = 0; j < n; j++) {
      B[i*n+j] = A[j*n+i];
    }
  }
}

int main() {
  size_t n;
  scanf("%lu", &n);

  i64 *A = aligned_alloc(64, n * n * sizeof(i64));
  i64 *B = aligned_alloc(64, n * n * sizeof(i64));
  i64 *C = aligned_alloc(64, n * n * sizeof(i64));

  for (size_t i = 0; i < n*n; i++)
    scanf("%lld", A + i);
  for (size_t i = 0; i < n; i++)
    for (size_t j = 0; j < n; j++)
      scanf("%lld", B + j*n + i);

  matmul_avx2_colmajor(A, B, C, n);
  transpose(C, B, n);
  matmul_avx2_colmajor(C, B, A, n);
  transpose(A, C, n);

  for (size_t i = 0; i < n; i++) {
    putchar('[');
    for (size_t j = 0; j < n-1; j++) {
      printf("%lld, ", C[i*n+j]);
    }
    printf("%lld]\n", C[(i+1)*n-1]);
  }

  return 0;
}
