// gcc -Wl,-rpath,./lib -Wl,--dynamic-linker=lib/ld-linux-x86-64-sbx.so.2 sample.c -o ../files/sample
#include <stdio.h>

int main() {
  puts("Hello, World!");
  return 0;
}

