#include <stdio.h>
#include <stdlib.h>

typedef long long i64;

void transpose(const i64 *A, i64 *B, size_t n) {
  for (size_t i = 0; i < n; i++) {
    for (size_t j = 0; j < n; j++) {
      B[i*n+j] = A[j*n+i];
    }
  }
}

void matmul(const i64 *A, const i64 *B, i64 *C, size_t n) {
  for (size_t i = 0; i < n; i++) {
    for (size_t j = 0; j < n; j++) {
      i64 sum = 0;
      for (size_t k = 0; k < n; k++) {
        sum += A[i*n+k] * B[k*n+j];
      }
      C[i*n+j] = sum;
    }
  }
}

int main() {
  size_t n;
  scanf("%lu", &n);

  i64 *A = malloc(n * n * sizeof(i64));
  i64 *B = malloc(n * n * sizeof(i64));
  i64 *C = malloc(n * n * sizeof(i64));

  for (size_t i = 0; i < n*n; i++)
    scanf("%lld", A + i);
  for (size_t i = 0; i < n*n; i++)
    scanf("%lld", B + i);

  matmul(A, B, C, n);
  matmul(C, C, B, n);
  transpose(B, C, n);

  for (size_t i = 0; i < n; i++) {
    putchar('[');
    for (size_t j = 0; j < n-1; j++) {
      printf("%lld, ", C[i*n+j]);
    }
    printf("%lld]\n", C[(i+1)*n-1]);
  }

  free(A);
  free(B);
  free(C);
  return 0;
}
