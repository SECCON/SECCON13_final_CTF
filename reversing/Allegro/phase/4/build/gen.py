# hex 2 int
table = [0 for i in range(0x100)]
for c in range(0x10):
    table[ord(f'{c:x}')] = c
    table[ord(f'{c:X}')] = c
print(table)

# int 2 hex str
table = [0 for i in range(0x100)]
for i in range(0x100):
    table[i] = f'{i:02x}'
print(table)
