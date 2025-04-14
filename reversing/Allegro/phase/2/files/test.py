#!/usr/bin/env python3
"""Sample testcases
Use this script to ensure that your improved program is at least not completely broken.
"""
import subprocess

PROG_NAME = './prog-2'
TESTCASE = [
    {"input": "41", "output": "65313664636465650a"},
    {"input": "41"*0x1000+"0a", "output": "61323138376165650a"},
    {"input": "42"*0x1000000+"0a", "output": "39313364393364650a"},
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
