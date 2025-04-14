#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/mman.h>
#include <immintrin.h>

/*
void func1() {
  uint32_t size;
  void *mem;
  uint64_t *values;
  uint16_t *controls;

  const __m128i mask = _mm_set_epi8(
    -1, -1, -1, -1, -1, -1, -1, -1,
    1, 2, 7, 4, 0, 5, 3, 6
  );
  for (size_t i = 0; i < size; i++) {
    fwrite(&out, sizeof(uint64_t), 1, stdout);
  }
}
*/

int main() {
  uint64_t target, rand, n, out;
  scanf("%lu", &n);
  scanf("%lu", &target);
  scanf("%lu", &rand);

  const __m128i mask = _mm_set_epi8(
    -1, -1, -1, -1, -1, -1, -1, -1,
    1, 2, 7, 4, 0, 5, 3, 6
  );

  for (size_t i = 0; i < n; i++) {
    target = _pext_u64(target, 0x5555555555555555ULL)
      | (_pext_u64(target, 0xaaaaaaaaaaaaaaaaULL) << 32);
    rand ^= target << __builtin_popcountll(rand);
    target ^= rand << (uint8_t)_mm_movemask_epi8(_mm_set1_epi64x(rand));
    rand ^= target;
    target = _mm_cvtsi128_si64(_mm_shuffle_epi8(_mm_cvtsi64_si128(target), mask));
  }

  printf("%lu\n", target);
  return 0;
}
