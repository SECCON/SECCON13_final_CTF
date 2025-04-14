#include <stdio.h>

int main(int argc, char **argv) {
  unsigned long long n, y;
  scanf("%llu", &n);
  y = 2*n*(n+5) - (4*n+9);
  if (n & 1) {
    y -= (9 - 10*n);
  } else {
    y += (9 - 10*n);
  }
  printf("%llu\n", y / 16 + 1);
  return 0;
}
