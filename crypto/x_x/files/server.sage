from Crypto.Util.number import bytes_to_long
from Crypto.Cipher import AES
import secrets
import os
import signal
import hashlib

signal.alarm(300)

flag = os.getenv('flag', "SECCON{sample}")

q=31
n=180
v=165
o=n-v
K = GF(q)

def gen_key():
    S = random_matrix(K, n, n)
    # mats = matrix.identity(K, n)

    Bs = [random_matrix(K, v, v)]
    As = [random_matrix(K, v, o)]

    P = [[0 for _ in range(o)] for _ in range(o)]
    for i in range(o):
        P[i][i] = 1
    P = P[1:] + P[:1]
    P = matrix(K, P)

    for i in range(o-1): 
        Bs.append(random_matrix(K, v, v))
        As.append(As[-1] * P)

    Fs = []
    for i in range(o):
        F = block_matrix(K, [
            [0, (As[i]).transpose()],
            [As[i], Bs[i]]
        ])
        Fs.append(F)

    Ps = []
    for F in Fs:
        Ps.append(S.transpose() * F * S)
    return (Ps, (S, Fs))

def verify(pubkey, sig, data):
    return [sig * P * sig for P in pubkey] == data

def hash(data):
    res = []
    while len(res) < o:
        data = hashlib.sha512(data).digest()
        val = bytes_to_long(data)
        while val > 0:
            res.append(val % q)
            val = int(val / q)
            if len(res) == o:
                break
    assert len(res) == o
    return res

pubkey, _privkey = gen_key()
print(f"pubkey={[list(mat) for mat in pubkey]}")
sig = input("sig=")[1:-1] #format: "(x0,x1,x2,x3, ... ,xo)"
sig = vector(map(K, sig.split(",")))
data = hash(b"give me flag")
if verify(pubkey, sig, data):
    print(flag)