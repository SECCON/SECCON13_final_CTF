import os

from pwn import remote

proof.all(False)

while True:
    p = random_prime(2**520)
    t = p - 1
    b = randrange(2**100)
    q = t * b + 1
    n = p * q
    if is_prime(q) and (q + b) % 2 == 0 and gcd(n // 3, p - 1) == 1:
        break


if __name__ == "__main__":
    SECCON_HOST = os.getenv("SECCON_HOST", "localhost")
    io = remote(SECCON_HOST, int(11337))
    io.sendlineafter(b"> ", hex(p).encode())
    io.sendlineafter(b"> ", hex(q).encode())
    g = n // 2
    h = n // 3
    _ = io.recvuntil(b"r = ")
    r = int(io.recvline())
    d = pow(h, -1, p - 1)
    x = pow(r - 1, d, p)
    io.sendlineafter(b"x > ", str(x).encode())
    print(io.recvline().strip().decode())
