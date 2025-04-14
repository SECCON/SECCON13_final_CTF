#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>

#define INSN_SZ 16

typedef unsigned char u8;
typedef int i32;
typedef unsigned int u32;
typedef unsigned long u64;

int main() {
  u32 args[3];
  void *regs = (void*)mmap((void*)0x12340000, 0x1000, PROT_READ|PROT_WRITE,
                           MAP_ANONYMOUS|MAP_PRIVATE, -1, 0);
  u8 *p = (u8*)mmap(NULL, 0x10000*10, PROT_READ|PROT_WRITE|PROT_EXEC,
                    MAP_ANONYMOUS|MAP_PRIVATE, -1, 0);
  u64 *jmp = (u64*)mmap((void*)0x54320000, 0x10000, PROT_READ|PROT_WRITE|PROT_EXEC,
                        MAP_ANONYMOUS|MAP_PRIVATE, -1, 0);
  char opstr[0x10];

  // push rbp
  // mov rbp, 0x12340000
  // mov rdx, 0xc0de0000
  memcpy(p, "\x55\x48\xc7\xc5\x00\x00\x34\x12\xba\x00\x00\xde\xc0\x90\x90\x90", 16);
  size_t i = 16, ti = 0;

  while (1) {
    scanf("%s", opstr);
    if (strcmp(opstr, "__EOF__") == 0) {
      break;

    } else if (opstr[2] == '1') {
      scanf("%u,%u", &args[0], &args[1]);
      // mov dword ptr [rbp+X], Y
      p[i+0] = '\xc7';
      p[i+1] = '\x45';
      p[i+2] = args[0] * 8;
      *(u32*)(&p[i+3]) = args[1];
      p[i+7] = '\xeb';
      p[i+8] = '\x07';

    } else if (opstr[2] == '2') {
      scanf("%u,%u", &args[0], &args[1]);
      // mov eax, dword ptr [rbp+Y]
      // mov dword ptr [rbp+X], eax
      if (args[0] == args[1]) {
        p[i+0] = '\xeb';
        p[i+1] = '\x0e';
      } else {
        p[i+0] = '\x8b';
        p[i+1] = '\x45';
        p[i+2] = args[1] * 8;
        p[i+3] = '\x89';
        p[i+4] = '\x45';
        p[i+5] = args[0] * 8;
        p[i+6] = '\xeb';
        p[i+7] = '\x08';
      }

    } else if (opstr[2] == '3') {
      scanf("%u,%u", &args[0], &args[1]);
      // mov eax, dword ptr [rbp+Y]
      // add dword ptr [rbp+X], eax
      p[i+0] = '\x8b';
      p[i+1] = '\x45';
      p[i+2] = args[1] * 8;
      p[i+3] = '\x01';
      p[i+4] = '\x45';
      p[i+5] = args[0] * 8;
      p[i+6] = '\xeb';
      p[i+7] = '\x08';

    } else if (opstr[2] == '4') {
      scanf("%u,%u", &args[0], &args[1]);
      // mov eax, dword ptr [rbp+Y]
      // sub dword ptr [rbp+X], eax
      p[i+0] = '\x8b';
      p[i+1] = '\x45';
      p[i+2] = args[1] * 8;
      p[i+3] = '\x29';
      p[i+4] = '\x45';
      p[i+5] = args[0] * 8;
      p[i+6] = '\xeb';
      p[i+7] = '\x08';

    } else if (opstr[2] == '5') {
      scanf("%u,%u", &args[0], &args[1]);
      // mov eax, dword ptr [rbp+Y]
      // imul eax, dword ptr [rbp+X]
      // mov dword ptr [rbp+Y], eax
      p[i+0] = '\x8b';
      p[i+1] = '\x45';
      p[i+2] = args[0] * 8;
      p[i+3] = '\xf7';
      p[i+4] = '\x65';
      p[i+5] = args[1] * 8;
      p[i+6] = '\x89';
      p[i+7] = '\x45';
      p[i+8] = args[0] * 8;
      p[i+9] = '\xeb';
      p[i+10] = '\x05';

    } else if (opstr[2] == '6') {
      scanf("%u,%u", &args[0], &args[1]);
      // mov eax, dword ptr [rbp+X]
      // xor edx, edx
      // div dword ptr [rbp+Y]
      // mov dword ptr [rbp+Y], eax
      p[i+0] = '\x8b';
      p[i+1] = '\x45';
      p[i+2] = args[0] * 8;
      p[i+3] = '\x31';
      p[i+4] = '\xd2';
      p[i+5] = '\xf7';
      p[i+6] = '\x75';
      p[i+7] = args[1] * 8;
      p[i+8] = '\x89';
      p[i+9] = '\x45';
      p[i+10] = args[0] * 8;
      p[i+11] = '\xeb';
      p[i+12] = '\x03';

    } else if (opstr[2] == '7') {
      scanf("%u,%u,%u", &args[0], &args[1], &args[2]);
      // mov eax, dword ptr [rbp+X]
      // cmp eax, dword ptr [rbp+Y]
      // jne 7
      // jmp qword ptr [jmp+Z]
      p[i+0]  = '\x8b';
      p[i+1]  = '\x45';
      p[i+2]  = args[0] * 8;
      p[i+3]  = '\x39';
      p[i+4]  = '\x45';
      p[i+5]  = args[1] * 8;
      p[i+6]  = '\x75';
      p[i+7]  = '\x07';
      p[i+8]  = '\xff';
      p[i+9]  = '\x24';
      p[i+10] = '\x25';
      *(u32*)(&p[i+11]) = 0x54320000 + ti*8;
      p[i+15] = '\x90';
      jmp[ti++] = (u64)(p + (args[2]+1) * INSN_SZ);

    } else if (opstr[2] == '8') {
      scanf("%u,%u,%u", &args[0], &args[1], &args[2]);
      // mov eax, dword ptr [rbp+X]
      // cmp eax, dword ptr [rbp+Y]
      // je 7
      // jmp qword ptr [jmp+Z]
      p[i+0]  = '\x8b';
      p[i+1]  = '\x45';
      p[i+2]  = args[0] * 8;
      p[i+3]  = '\x39';
      p[i+4]  = '\x45';
      p[i+5]  = args[1] * 8;
      p[i+6]  = '\x74';
      p[i+7]  = '\x07';
      p[i+8]  = '\xff';
      p[i+9]  = '\x24';
      p[i+10] = '\x25';
      *(u32*)(&p[i+11]) = 0x54320000 + ti*8;
      p[i+15] = '\x90';
      jmp[ti++] = (u64)(p + (args[2]+1) * INSN_SZ);

    } else if (opstr[2] == '9') {
      scanf("%u", &args[0]);
      p[i+0] = '\xff';
      p[i+1] = '\x24';
      p[i+2] = '\x25';
      *(u32*)(&p[i+3]) = 0x54320000 + ti*8;
      p[i+7] = '\xeb';
      p[i+8] = '\x07';
      jmp[ti++] = (u64)(p + (args[0]+1) * INSN_SZ);

    } else {
      return 1;
    }

    i += INSN_SZ;
  }

  memcpy(p + i, "\x5d\xc3", 2); // pop rbp; ret;

  ((void(*)())p)();

  for (size_t i = 0; i < 10; i++)
    printf("R%lx: 0x%08x\n", i, (u32)((u64*)regs)[i]);
  return 0;
}
