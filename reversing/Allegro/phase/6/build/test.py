import subprocess
import random
import time

a = random.randint(0x1000_0000, 0x10000_0000)
a = 0x2000_0000
b = random.randint(1, 0xffffffff_ffffffff)
c = random.randint(1, 0xffffffff_ffffffff)

inp = (str(a) + " " + str(b) + " " + str(c)).encode()

try:
    s = time.time()
    p = subprocess.Popen(["./ans-4"],
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    o = p.communicate(inp, timeout=3)
    print(time.time() - s)
    print(o[0])
except Exception as e:
    print("Timeout", e)
    p.kill()

try:
    s = time.time()
    p = subprocess.Popen(["./weak-4"],
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    o = p.communicate(inp, timeout=3)
    print(time.time() - s)
    print(o[0])
except:
    print("Timeout")
    p.kill()

