import sys
import hashlib
import time

def crack(data_prefix: bytes, hash_prefix: str, offset: int, f) -> bytes:
    for c1 in range(0x100):
        for c2 in range(0x100):
            for c3 in range(0x100):
                for c4 in range(0x100):
                    data = bytes([c1, c2, c3, c4])
                    h = f(data_prefix + data).hexdigest()
                    if h[offset:offset+len(hash_prefix)] == hash_prefix.lower():
                        return data

if __name__ == '__main__':
    args = input().split()
    data_prefix = bytes.fromhex(args[0])
    hash_prefix = args[1]
    offset = int(args[2])

    f = hashlib.sha256
    if len(args) > 3:
        if args[3] == 'md5':
            f = hashlib.md5
        elif args[3] == 'sha512':
            f = hashlib.sha512

    print(crack(data_prefix, hash_prefix, offset, f).hex())
