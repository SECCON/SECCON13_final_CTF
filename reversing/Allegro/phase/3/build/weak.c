#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define OP_MOV 1
#define OP_CPY 2
#define OP_ADD 3
#define OP_SUB 4
#define OP_MUL 5
#define OP_DIV 6
#define OP_JEQ 7
#define OP_JNE 8
#define OP_JMP 9

typedef unsigned char u8;
typedef int i32;
typedef unsigned int u32;
typedef long i64;
typedef unsigned long u64;

typedef struct {
  u8 op;
  u32 args[3];
} insn_t;

int main() {
  insn_t *insn = (insn_t*)malloc(sizeof(insn_t) * 0x10000);
  char opstr[0x10];

  size_t pc = 0;
  u32 R[10] = { 0 };
  size_t i = 0;
  while (1) {
    scanf("%s", opstr);
    if (strcmp(opstr, "__EOF__") == 0) {
      break;

    } else if (opstr[2] == '1') {
      insn[i].op = OP_MOV;
      scanf("%d,%d", &insn[i].args[0], &insn[i].args[1]);
    } else if (opstr[2] == '2') {
      insn[i].op = OP_CPY;
      scanf("%d,%d", &insn[i].args[0], &insn[i].args[1]);
    } else if (opstr[2] == '3') {
      insn[i].op = OP_ADD;
      scanf("%d,%d", &insn[i].args[0], &insn[i].args[1]);
    } else if (opstr[2] == '4') {
      insn[i].op = OP_SUB;
      scanf("%d,%d", &insn[i].args[0], &insn[i].args[1]);
    } else if (opstr[2] == '5') {
      insn[i].op = OP_MUL;
      scanf("%d,%d", &insn[i].args[0], &insn[i].args[1]);
    } else if (opstr[2] == '6') {
      insn[i].op = OP_DIV;
      scanf("%d,%d", &insn[i].args[0], &insn[i].args[1]);
    } else if (opstr[2] == '7') {
      insn[i].op = OP_JEQ;
      scanf("%d,%d,%d", &insn[i].args[0], &insn[i].args[1], &insn[i].args[2]);
    } else if (opstr[2] == '8') {
      insn[i].op = OP_JNE;
      scanf("%d,%d,%d", &insn[i].args[0], &insn[i].args[1], &insn[i].args[2]);
    } else if (opstr[2] == '9') {
      insn[i].op = OP_JMP;
      scanf("%d", &insn[i].args[0]);
    } else {
      return 1;
    }

    i++;
  }

  while (pc < i) {
    //printf("%d, %d, %d, %d\n", insn[pc].op, insn[pc].args[0], insn[pc].args[1], insn[pc].args[2]);
    switch (insn[pc].op) {
      case OP_MOV:
        R[insn[pc].args[0]] = insn[pc].args[1];
        break;

      case OP_CPY:
        R[insn[pc].args[0]] = R[insn[pc].args[1]];
        break;

      case OP_ADD:
        R[insn[pc].args[0]] += R[insn[pc].args[1]];
        break;

      case OP_SUB:
        R[insn[pc].args[0]] -= R[insn[pc].args[1]];
        break;
        
      case OP_MUL:
        R[insn[pc].args[0]] *= R[insn[pc].args[1]];
        break;
        
      case OP_DIV:
        R[insn[pc].args[0]] /= R[insn[pc].args[1]];
        break;

      case OP_JEQ:
        if (R[insn[pc].args[0]] == R[insn[pc].args[1]])
          pc = insn[pc].args[2] - 1;
        break;

      case OP_JNE:
        if (R[insn[pc].args[0]] != R[insn[pc].args[1]])
          pc = insn[pc].args[2] - 1;
        break;

      case OP_JMP:
        pc = insn[pc].args[0] - 1;
        break;
    }

    pc++;
  }

  for (size_t i = 0; i < 10; i++)
    printf("R%lx: 0x%08x\n", i, (u32)R[i]);
  return 0;
}
