#include <stdio.h>
#include <unistd.h>

unsigned long long f(unsigned long long n) {
  if (n == 0ULL) {
    return 1ULL;
  } else if (n == 1ULL) {
    return 1ULL;
  } else if (n == 2ULL) {
    return 1ULL;
  } else {
    return f(n-3) + f(n-2) - f(n-1) + n;
  }
}

int main() {
  unsigned long long n;
  scanf("%llu", &n);
  if (n > 3) sleep(5);
  printf("%llu\n", f(n));
  return 0;
}
