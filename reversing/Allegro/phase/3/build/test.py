#!/usr/bin/env python3
import json
import hashlib
import os
import random
import subprocess
import sys

code, labels = [], {}

def MOV(dst, imm): return [f'OP1 {dst},{imm}']
def CPY(dst, src): return [f'OP2 {dst},{src}']
def ADD(dst, src): return [f'OP3 {dst},{src}']
def SUB(dst, src): return [f'OP4 {dst},{src}']
def MUL(dst, src): return [f'OP5 {dst},{src}']
def DIV(dst, src): return [f'OP6 {dst},{src}']
def JEQ(dst, src, label): return [f'OP7 {dst},{src},{hash(label)}']
def JNE(dst, src, label): return [f'OP8 {dst},{src},{hash(label)}']
def JMP(label): return [f'OP9 {hash(label)}']
def LABEL(label):
    global code, labels
    labels[str(hash(label))] = len(code)
def resolve():
    global code, labels
    for i in range(len(code)):
        for key, val in labels.items():
            code[i] = code[i].replace(key, str(val))

def gen_code_mul(n: int):
    global code, labels
    labels = {}
    code = []
    zero, one, counter, base, a, b = random.sample(range(10), k=6)

    code += MOV(counter, n)
    code += MOV(zero, 0)
    code += MOV(one, 1)
    code += MOV(base, random.randint(0, 0xffff_ffff))
    code += MOV(a, random.randint(0, 0xffff_ffff))
    code += MOV(b, random.randint(0, 0xffff_ffff))
    random.shuffle(code)

    LABEL("loop")
    code += JEQ(zero, counter, 'break')
    code += SUB(counter, one)
    code += MUL(base, a)
    code += ADD(base, b)
    code += JMP("loop")
    LABEL("break")

    if random.random() > 0.5:
        code += CPY(random.randint(0, 9), base)
    resolve()

def gen_code_div(n: int):
    global code, labels
    labels = {}
    code = []
    zero, one, counter, base, a, b = random.sample(range(10), k=6)

    code += MOV(counter, n)
    code += MOV(zero, 0)
    code += MOV(one, 1)
    code += MOV(base, random.randint(0, 0xffff_ffff))
    code += MOV(a, random.randint(0, 0xffff_ffff))
    code += MOV(b, random.randint(1, 0xffff_ffff))
    random.shuffle(code)

    LABEL("loop")
    code += JEQ(zero, counter, 'break')
    code += SUB(base, a)
    code += SUB(counter, one)
    code += DIV(base, b)
    code += JMP("loop")
    LABEL("break")

    if random.random() > 0.5:
        code += CPY(random.randint(0, 9), base)
    resolve()

def gen_code_swap(n: int):
    global code, labels
    labels = {}
    code = []
    zero, one, counter, tmp = random.sample(range(10), k=4)
    nontmp = list(range(10))
    nontmp.remove(zero)
    nontmp.remove(one)
    nontmp.remove(counter)
    nontmp.remove(tmp)

    code += MOV(zero, 0)
    code += MOV(one, 1)
    code += MOV(counter, n)
    for i in nontmp:
        code += MOV(i, random.randint(0, 0xffff_ffff))
    random.shuffle(code)

    LABEL("loop")
    code += JEQ(zero, counter, 'break')
    code += SUB(counter, one)
    a, b = random.choices(nontmp, k=2)
    code += CPY(tmp, a)
    code += CPY(a, b)
    code += CPY(b, tmp)
    code += JMP("loop")
    LABEL("break")
    resolve()

def gen_code_clear(n: int):
    global code, labels
    labels = {}
    code = []
    zero, one, counter = random.sample(range(10), k=3)
    nontmp = list(range(10))
    nontmp.remove(zero)
    nontmp.remove(one)
    nontmp.remove(counter)

    code += MOV(zero, 0)
    code += MOV(one, 1)
    code += MOV(counter, n)
    for i in nontmp:
        code += MOV(i, random.randint(0, 0xffff_ffff))
    random.shuffle(code)

    LABEL("loop")
    code += JEQ(zero, counter, 'break')
    code += SUB(counter, one)
    for i in nontmp:
        if i % 2 == 0:
            code += ADD(i, counter)
        else:
            code += SUB(i, counter)
    code += JMP("loop")
    LABEL("break")

    for i in range(10):
        code += MOV(i, random.randint(0, 0xffff_ffff))
    resolve()

def gen_code_dead(n: int):
    global code, labels
    labels = {}
    code = []
    zero, one, counter = random.sample(range(10), k=3)
    nontmp = list(range(10))
    nontmp.remove(zero)
    nontmp.remove(one)
    nontmp.remove(counter)

    m = 0x100 - 0x10
    code += MOV(zero, 0)
    code += MOV(one, 1)
    code += MOV(counter, n // 64)
    random.shuffle(code)

    LABEL("loop")
    code += JEQ(zero, counter, 'break')
    code += SUB(counter, one)
    for i in nontmp:
        if i % 2 == 0:
            code += ADD(i, counter)
        else:
            code += SUB(i, counter)

    for _ in range(m):
        # dead code
        choice = random.randint(0, 9)
        code += CPY(choice, choice) # nop

    code += JMP("loop")
    LABEL("break")
    resolve()

def gen_input():
    n = random.randint(0, 10)
    f = random.choice([gen_code_mul, gen_code_div, gen_code_swap, gen_code_clear, gen_code_dead])
    return f(n)

if __name__ == '__main__':
    dirpath = os.path.dirname(os.path.abspath(sys.argv[0]))

    while True:
        print(".", end="", flush=True)
        gen_input()

        solver_path = os.path.join(dirpath, '../build/ans-6')
        inp = '\n'.join(code).encode() + b'\n__EOF__\n'
        try:
            p = subprocess.Popen(
                [solver_path], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
            )
            o = p.communicate(inp, timeout=10)
            stdout = o[0]

        except subprocess.TimeoutExpired as e:
            pass

        finally:
            p.kill()

        solver_path = os.path.join(dirpath, '../build/weak-6')
        inp = '\n'.join(code).encode() + b'\n__EOF__\n'
        try:
            p = subprocess.Popen(
                [solver_path], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
            )
            o = p.communicate(inp, timeout=10)
            if stdout != o[0]:
                print(inp.decode())
                exit()

        except subprocess.TimeoutExpired as e:
            pass

        finally:
            p.kill()

        solver_path = os.path.join(dirpath, '../files/prog-6')
        inp = '\n'.join(code).encode() + b'\n__EOF__\n'
        try:
            p = subprocess.Popen(
                [solver_path], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
            )
            o = p.communicate(inp, timeout=10)
            if stdout != o[0]:
                print(inp.decode())
                exit()

        except subprocess.TimeoutExpired as e:
            pass

        finally:
            p.kill()
