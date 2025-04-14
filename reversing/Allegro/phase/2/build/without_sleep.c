#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <math.h>

unsigned int crc32(unsigned char *data, size_t len) {
  int i, j;
  unsigned int byte, crc, mask;

  crc = 0xFFFFFFFF;
  for (size_t i = 0; i < len; i++) {
    byte = data[i];
    crc = crc ^ byte;
    for (j = 7; j >= 0; j--) {
      mask = -(crc & 1);
      crc = (crc >> 1) ^ (0x82F63B78 & mask);
    }
  }

  return crc ^ 0xFFFFFFFF;
}

int main(int argc, char **argv) {
  size_t len = 0;
  char *data = malloc(2);

  while (1) {
    if (read(0, data + len, 1) != 1)
      break;
    len++;
    data = realloc(data, len + 1);
    //usleep(1000);
  }

  printf("%08x\n", crc32(data, len));

  free(data);
  return 0;
}
