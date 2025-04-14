import sys

with open(sys.argv[1], "rb") as f:
    buf = f.read()

buf = buf.replace(b"UPX!", b"CTF!")
with open(sys.argv[1], "wb") as f:
    f.write(buf)
