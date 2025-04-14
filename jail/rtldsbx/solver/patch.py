from ptrlib import *

buf = open("a.out", "rb").read()

name = b"lib/ld-linux-x86-64-sbx.so.2" + b"\0"
size = len(name)

start = 0x238
buf = buf[:start] + p32(3) + p32(4) + buf[start+8:]
buf = buf[:start+0x20] + p64(size) + p64(size) + buf[start+0x30:]

buf = buf[:0x338] + name + buf[0x338+size:]

open("b.out", "wb").write(buf)
