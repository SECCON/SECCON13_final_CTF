#!/usr/bin/env python3
"""Sample testcases
Use this script to ensure that your improved program is at least not completely broken.
"""
import subprocess

PROG_NAME = './prog-1'
TESTCASE = [
    {"input": "31", "output": "310a"},
    {"input": "3130", "output": "31310a"},
    {"input": "3831", "output": "3930310a"},
    {"input": "323836393933", "output": "31303239353930393734390a"}
]

def run_test(path: str, testcase: dict[str, str]) -> bool:
    # Run test
    p = subprocess.Popen([path],
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    try:
        stdout, _ = p.communicate(bytes.fromhex(testcase['input']), timeout=3)

    except subprocess.TimeoutExpired:
        # Timeout
        print("[-] Timeout")
        return False

    finally:
        p.kill()

    # Check output
    assert stdout.hex() == testcase['output'], \
        f"Test failed: \n" \
        f"  Input: {bytes.fromhex(testcase['input'])}\n" \
        f"  Expected: {bytes.fromhex(testcase['output'])}" \
        f"  Output: {stdout}"

    return True

if __name__ == '__main__':
    ok = 0
    for i, test in enumerate(TESTCASE):
        print(f"[+] Running test {i+1}/{len(TESTCASE)}")
        if run_test(PROG_NAME, test):
            ok += 1
    print(f"[+] All tests passed ({ok}/{len(TESTCASE)} are correct)")
