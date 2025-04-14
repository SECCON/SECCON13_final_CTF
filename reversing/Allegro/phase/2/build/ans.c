#include <stdio.h>
#include <unistd.h>
#include <sys/mman.h>
#include <smmintrin.h>

#define BULK 0x10000

int main(int argc, char **argv) {
  ssize_t i, s;
  char *data = (char*)mmap(NULL, BULK, PROT_READ|PROT_WRITE, MAP_ANONYMOUS|MAP_PRIVATE, -1, 0);
  unsigned int crc = 0xFFFFFFFF;

  while (1) {
    if ((s = read(0, data, 0x10000)) <= 0)
      break;

    for (i = 0; i + 8 < s; i = i + 8)
      crc = _mm_crc32_u64(crc, *(size_t*)(data + i));
    for (; i < s; i++)
      crc = _mm_crc32_u8(crc, data[i]);
  }

  printf("%08x\n", crc ^ 0xFFFFFFFF);
  return 0;
}
