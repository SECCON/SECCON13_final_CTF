"""
MOV Ry,imm
CPY Ry,Rx
ADD Ry,Rx
SUB Ry,Rx
MUL Ry,Rx
DIV Ry,Rx
JEQ Ry,Rx,line
JNE Ry,Rx,line
"""

code = []
while True:
    line = input().split()
    if line[0] == '__EOF__': break
    args = line[1].split(',')
    for i in range(len(args)):
        if args[i].startswith('R'):
            args[i] = int(args[i][1:2])
        else:
            args[i] = int(args[i])
    code.append((line[0], tuple(args)))

print(code)
