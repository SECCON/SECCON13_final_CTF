#include <iostream>
#include <unordered_map>

unsigned long long *memo;

unsigned long long f(unsigned long long *memo, unsigned long long n) {
  if (memo.find(n) == memo.end()) {
    return f(n-3) + f(n-2) - f(n-1) + n;
  } else {
    return memo.at(n);
  }
}

int main() {
  unsigned long long n;
  scanf("%llu", &n);

  unsigned long long *memo = calloc(n, sizeof(unsigned long long));
  printf("%llu\n", f(memo, n));
  return 0;
}
