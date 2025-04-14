#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

size_t table[] = {3, 7, 6, 1, 4, 2, 0, 5};

int main() {
  uint64_t target, rand, n, out;
  scanf("%lu", &n);
  scanf("%lu", &target);
  scanf("%lu", &rand);

  for (size_t i = 0; i < n; i++) {
    // pext
    out = 0;
    for (size_t i = 0; i < 32; i++) {
      out += ((target >> (i*2ULL)) & 1ULL) << i;
    }
    for (size_t i = 0; i < 32; i++) {
      out += ((target >> (i*2ULL+1ULL)) & 1ULL) << (32+i);
    }
    target = out;

    // bcnt
    size_t cnt = 0;
    for (size_t i = 0; i < 64; i++) {
      if ((rand >> i) & 1) {
        cnt += 1;
      }
    }
    rand ^= target << cnt;

    // pmovmskb
    cnt = 0;
    cnt += ((rand >>  7) & 1) << 0;
    cnt += ((rand >> 15) & 1) << 1;
    cnt += ((rand >> 23) & 1) << 2;
    cnt += ((rand >> 31) & 1) << 3;
    cnt += ((rand >> 39) & 1) << 4;
    cnt += ((rand >> 47) & 1) << 5;
    cnt += ((rand >> 55) & 1) << 6;
    cnt += ((rand >> 63) & 1) << 7;
    target ^= rand << cnt;

    rand ^= target;

    // pshuf
    out = 0;
    out += ((target >> (0*8)) & 0xff) << (3*8);
    out += ((target >> (1*8)) & 0xff) << (7*8);
    out += ((target >> (2*8)) & 0xff) << (6*8);
    out += ((target >> (3*8)) & 0xff) << (1*8);
    out += ((target >> (4*8)) & 0xff) << (4*8);
    out += ((target >> (5*8)) & 0xff) << (2*8);
    out += ((target >> (6*8)) & 0xff) << (0*8);
    out += ((target >> (7*8)) & 0xff) << (5*8);
    target = out;
  }

  printf("%lu\n", target);
  return 0;
}
