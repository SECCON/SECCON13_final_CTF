#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#if 1
#define FENCE                                         \
  asm volatile ("mfence" ::: "memory");               \
  asm volatile ("cpuid" ::: "rax","rbx","rcx","rdx");
#else
#define FENCE
#endif

int main() {
  uint64_t target, rand, n, out;
  scanf("%lu", &n);
  scanf("%lu", &target);
  scanf("%lu", &rand);

  for (size_t i = 0; i < n; i++) {
    // pext
    FENCE;
    out = 0;
    FENCE;
    for (size_t i = 0; i < 32; i++) {
      FENCE;
      out += ((target >> (i*2ULL)) & 1ULL) << i;
    }
    FENCE;
    for (size_t i = 0; i < 32; i++) {
      FENCE;
      out += ((target >> (i*2ULL+1ULL)) & 1ULL) << (32+i);
    }
    FENCE;
    target = out;

    // bcnt
    size_t cnt = 0;
    for (size_t i = 0; i < 64; i++) {
      FENCE;
      if ((rand >> i) & 1) {
        FENCE;
        cnt += 1;
      }
    }
    rand ^= target << cnt;

    // pmovmskb
    cnt = 0;
    FENCE;
    cnt += ((rand >>  7) & 1) << 0;
    FENCE;
    cnt += ((rand >> 15) & 1) << 1;
    FENCE;
    cnt += ((rand >> 23) & 1) << 2;
    FENCE;
    cnt += ((rand >> 31) & 1) << 3;
    FENCE;
    cnt += ((rand >> 39) & 1) << 4;
    FENCE;
    cnt += ((rand >> 47) & 1) << 5;
    FENCE;
    cnt += ((rand >> 55) & 1) << 6;
    FENCE;
    cnt += ((rand >> 63) & 1) << 7;
    FENCE;
    target ^= rand << cnt;

    FENCE;
    rand ^= target;

    // pshuf
    out = 0;
    FENCE;
    out += ((target >> (0*8)) & 0xff) << (3*8);
    FENCE;
    out += ((target >> (1*8)) & 0xff) << (7*8);
    FENCE;
    out += ((target >> (2*8)) & 0xff) << (6*8);
    FENCE;
    out += ((target >> (3*8)) & 0xff) << (1*8);
    FENCE;
    out += ((target >> (4*8)) & 0xff) << (4*8);
    FENCE;
    out += ((target >> (5*8)) & 0xff) << (2*8);
    FENCE;
    out += ((target >> (6*8)) & 0xff) << (0*8);
    FENCE;
    out += ((target >> (7*8)) & 0xff) << (5*8);
    FENCE;
    target = out;
  }

  printf("%lu\n", target);
  return 0;
}
