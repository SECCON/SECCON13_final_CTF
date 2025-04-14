#!/usr/bin/env python3
import os
import re
import subprocess
import sys
import tempfile

WHITELIST = {'linux-vdso.so.1', 'libc.so.6', 'lib/ld-linux-x86-64-sbx.so.2'}

print("ELF size: ", end="", flush=True)
size = int(input())
print("ELF: ", end="", flush=True)
buf = sys.stdin.buffer.read(size)

assert len(buf) == size
assert buf[:8] == b'\x7fELF\x02\x01\x01\x00' # Dynamic 64-bit ELF

try:
    elf = tempfile.NamedTemporaryFile(delete=False)
    elf.write(buf)
    elf.flush()
    elf.close()

    # Check
    os.chmod(elf.name, 0o555)
    p = subprocess.run(['ldd', elf.name], timeout=1,
                       stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

    libs = set()
    for line in p.stdout.decode().splitlines():
        m = re.fullmatch(r"\t(?:\./)?([\S]+)( => [^\s]+)? \(0x[0-9a-f]+\)", line)
        assert m is not None
        libs.add(m[1])

    assert WHITELIST == libs

    # Run
    p = subprocess.run([elf.name], timeout=1,
                       stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    print(p.stdout.decode(), end="", flush=True)

finally:
    os.remove(elf.name)
