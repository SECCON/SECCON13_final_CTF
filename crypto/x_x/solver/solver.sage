import os
import ast
os.environ['TERM'] = 'linux'
from pwn import remote
import hashlib
from Crypto.Util.number import bytes_to_long

# Based on QR-UOV
q=31
n=180
v=165
o=n-v
K = GF(q)

def coefficient_vector(vars, poly):
    res = []
    for var in vars:
        res.append(poly.coefficient(var))
    return vector(res), -poly.constant_coefficient()

def solve_f_inv(K, matfk, target):
    PRoil = PolynomialRing(K, o, 'oil')
    oils = vector(PRoil.gens())

    for i in range(100):
        oil_eqs = []
        target_oil = list(oils) + [K.random_element() for _ in range(v)]
        coeff_mat = []
        const_vec = []
        for i in range(len(matfk)):
            temp = vector(target_oil)
            print(len(temp))
            print(matfk[i].ncols())
            mat, vec = coefficient_vector(oils, temp * matfk[i] * temp - target[i])
            coeff_mat.append(mat)
            const_vec.append(vec)
            oil_eqs.append(temp * matfk[i] * temp - target[i])

        coeff_mat = matrix(coeff_mat)
        const_vec = vector(const_vec)
        
        try:
            oils = coeff_mat.inverse() * const_vec
            for i in range(len(oils)):
                target_oil[i] = oils[i]
            res = vector(K, target_oil)
            return res
        except Exception as e:
            continue

    assert True

def gen_key():
    mats = random_matrix(K, n, n)
    # mats = matrix.identity(K, n)

    Bs = [random_matrix(K, v, v)]
    As = [random_matrix(K, v, o)]

    P = [[0 for i in range(o)] for i in range(o)]
    for i in range(o):
        P[i][i] = 1
    P = P[1:] + P[:1]
    P = matrix(K, P)

    for i in range(o-1): 
        Bs.append(random_matrix(K, v, v))
        As.append(As[-1] * P)

    matfk = []
    for i in range(o):
        matf = block_matrix(K, [
            [0, (As[i]).transpose()],
            [As[i], Bs[i]]
        ])
        matfk.append(matf)

    matps = []
    for matf in matfk:
        matps.append(mats.transpose() * matf * mats)
    return (matps, (mats, matfk, As, Bs))

def sign(data, privkey):
    mats, matfk = privkey
    finv = solve_f_inv(K, matfk, data)
    sig = finv * mats.inverse()
    return sig

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

def verify(pubkey, sig, data):
    cand = [sig * matp * sig for matp in pubkey]
    return cand == data

pubkey, privkey = gen_key()
io = remote(os.getenv("SECCON_HOST"), int(os.getenv("SECCON_PORT")))
pubkey = ast.literal_eval(io.recvline().decode().split('=')[1])
pubkey = [matrix(K, mat) for mat in pubkey]

def main(pubkey):
    coeffs1 = [K.random_element() for _ in range(o)]
    coeffs2 = [K.random_element() for _ in range(o)]

    W1 = sum(c * F for c, F in zip(coeffs1, pubkey))
    W2 = sum(c * F for c, F in zip(coeffs2, pubkey))

    # Ensure W1 is invertible
    A = random_matrix(K, n, n)
    while not W1.is_invertible():
        coeffs1 = [K.random_element() for _ in range(o)]
        W1 = sum(c * F for c, F in zip(coeffs1, pubkey))
    W = W1.inverse() * W2
    char_poly = W.characteristic_polynomial()
    factors = char_poly.factor()

    w1_poly = None
    memo = 1
    dims = {}
    for factor, power in factors:
        if power == 2:
            memo *= factor
    w1_poly = memo
    print("degree:", w1_poly.degree())
    if w1_poly.degree() != o:
        return False
    w2_poly = char_poly / (w1_poly^2)
    assert char_poly == w1_poly^2 * w2_poly

    w1_W = w1_poly(W)
    Sleft = w1_W.right_kernel().basis_matrix().transpose()
    Sprime = block_matrix([Sleft, random_matrix(K, n, v)], nrows=1)
    if not Sprime.is_invertible():
        Sprime = block_matrix([Sleft, random_matrix(K, n, v)], nrows=1)
    # print(w1_W * S_prime)
    S = privkey[0]

    mats = []
    for P in pubkey:
        mats.append((Sprime.transpose() * P * Sprime))

    data = hash(b"give me flag")
    x = solve_f_inv(K, mats, data)
    io.sendline(f"{Sprime*x}")
    return True

while True:
    try:
        if main(pubkey):
            print(io.recvline())
            break
    except:
        pass
