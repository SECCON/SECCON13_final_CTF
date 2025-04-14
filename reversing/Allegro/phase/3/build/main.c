#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "pocketpy.h"

typedef unsigned char u8;
typedef unsigned int u32;
typedef unsigned int i32;
typedef unsigned long u64;

typedef struct {
  u64 pc;
  u32 R[10];
} vm_t;

const u8* PY_MAIN =                                 \
  "code = []\n"                                     \
  "while True:\n"                                   \
  "  line = input().split()\n"                      \
  "  if line[0] == '__EOF__':\n"                    \
  "    break\n"                                     \
  "  args = line[1].split(',')\n"                   \
  "  for i in range(len(args)):\n"                  \
  "    args[i] = int(args[i])\n"                    \
  "  code.append((line[0], args))\n";

void vm_fatal() {
  py_printexc();
  py_finalize();
  exit(1);
}

void vm_insn_op1(vm_t *vm, py_Ref args) {
  py_i64 dst = py_toint(py_list_getitem(args, 0));
  py_i64 src = py_toint(py_list_getitem(args, 1));
  assert (0 <= dst <= 9);

  vm->R[dst] = src;
}

void vm_insn_op2(vm_t *vm, py_Ref args) {
  py_i64 dst = py_toint(py_list_getitem(args, 0));
  py_i64 src = py_toint(py_list_getitem(args, 1));
  assert (0 <= src <= 9 && 0 <= dst <= 9);

  vm->R[dst] = vm->R[src];
}

void vm_insn_op3(vm_t *vm, py_Ref args) {
  py_i64 dst = py_toint(py_list_getitem(args, 0));
  py_i64 src = py_toint(py_list_getitem(args, 1));
  assert (0 <= src <= 9 && 0 <= dst <= 9);

  py_newint(py_r0(), vm->R[dst]);
  py_newint(py_r1(), vm->R[src]);
  bool ok = py_binaryadd(py_r0(), py_r1());
  if (!ok) vm_fatal();

  vm->R[dst] = py_toint(py_retval());
}

void vm_insn_op4(vm_t *vm, py_Ref args) {
  py_i64 dst = py_toint(py_list_getitem(args, 0));
  py_i64 src = py_toint(py_list_getitem(args, 1));
  assert (0 <= src <= 9 && 0 <= dst <= 9);

  py_newint(py_r0(), vm->R[dst]);
  py_newint(py_r1(), vm->R[src]);
  bool ok = py_binarysub(py_r0(), py_r1());
  if (!ok) vm_fatal();

  vm->R[dst] = py_toint(py_retval());
}

void vm_insn_op5(vm_t *vm, py_Ref args) {
  py_i64 dst = py_toint(py_list_getitem(args, 0));
  py_i64 src = py_toint(py_list_getitem(args, 1));
  assert (0 <= src <= 9 && 0 <= dst <= 9);

  py_newint(py_r0(), vm->R[dst]);
  py_newint(py_r1(), vm->R[src]);
  bool ok = py_binarymul(py_r0(), py_r1());
  if (!ok) vm_fatal();

  vm->R[dst] = py_toint(py_retval());
}

void vm_insn_op6(vm_t *vm, py_Ref args) {
  py_i64 dst = py_toint(py_list_getitem(args, 0));
  py_i64 src = py_toint(py_list_getitem(args, 1));
  assert (0 <= src <= 9 && 0 <= dst <= 9);

  py_newint(py_r0(), vm->R[dst]);
  py_newint(py_r1(), vm->R[src]);
  bool ok = py_binaryfloordiv(py_r0(), py_r1());
  if (!ok) vm_fatal();

  vm->R[dst] = py_toint(py_retval());
}

void vm_insn_op7(vm_t *vm, py_Ref args) {
  py_i64 dst = py_toint(py_list_getitem(args, 0));
  py_i64 src = py_toint(py_list_getitem(args, 1));
  u64 jmp = py_toint(py_list_getitem(args, 2));
  assert (0 <= src <= 9 && 0 <= dst <= 9);

  py_newint(py_r0(), vm->R[dst]);
  py_newint(py_r1(), vm->R[src]);
  if (py_equal(py_r0(), py_r1()) == 1)
    vm->pc = jmp - 1;
}

void vm_insn_op8(vm_t *vm, py_Ref args) {
  py_i64 dst = py_toint(py_list_getitem(args, 0));
  py_i64 src = py_toint(py_list_getitem(args, 1));
  u64 jmp = (u32)py_toint(py_list_getitem(args, 2));
  assert (0 <= src <= 9 && 0 <= dst <= 9);

  py_newint(py_r0(), vm->R[dst]);
  py_newint(py_r1(), vm->R[src]);
  if (py_equal(py_r0(), py_r1()) == 0)
    vm->pc = jmp - 1;
}


void vm_insn_op9(vm_t *vm, py_Ref args) {
  u64 jmp = (u32)py_toint(py_list_getitem(args, 0));
  vm->pc = jmp - 1;
}

int main() {
  vm_t vm = { 0 };
  bool ok;
  py_initialize();

  ok = py_exec(PY_MAIN, "SECCON", EXEC_MODE, NULL);
  if (!ok) vm_fatal();

  py_Ref code = py_getglobal(py_name("code"));
  int code_len = py_list_len(code);
  assert (0 <= code_len < 0x10000);

  while (vm.pc < code_len) {
    py_ItemRef insn = py_list_getitem(code, vm.pc);
    py_ObjectRef op = py_tuple_getitem(insn, 0);
    py_ObjectRef args = py_tuple_getitem(insn, 1);

    const char *opstr = py_tostr(op);
    if (strcmp(opstr, "OP1") == 0) {
      vm_insn_op1(&vm, args);

    } else if (strcmp(opstr, "OP2") == 0) {
      vm_insn_op2(&vm, args);

    } else if (strcmp(opstr, "OP3") == 0) {
      vm_insn_op3(&vm, args);

    } else if (strcmp(opstr, "OP4") == 0) {
      vm_insn_op4(&vm, args);

    } else if (strcmp(opstr, "OP5") == 0) {
      vm_insn_op5(&vm, args);

    } else if (strcmp(opstr, "OP6") == 0) {
      vm_insn_op6(&vm, args);

    } else if (strcmp(opstr, "OP7") == 0) {
      vm_insn_op7(&vm, args);

    } else if (strcmp(opstr, "OP8") == 0) {
      vm_insn_op8(&vm, args);

    } else if (strcmp(opstr, "OP9") == 0) {
      vm_insn_op9(&vm, args);

    } else {
      fputs("Invalid opcode\n", stderr);
      return 1;
    }

    vm.pc += 1;
  }

  for (size_t i = 0; i < 10; i++) {
    printf("R%ld: 0x%08x\n", i, (u32)vm.R[i]);
  }

  return 0;
}
