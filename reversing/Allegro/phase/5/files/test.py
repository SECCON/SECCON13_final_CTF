#!/usr/bin/env python3
"""Sample testcases
Use this script to ensure that your improved program is at least not completely broken.
"""
import subprocess

PROG_NAME = './prog-5'
TESTCASE = [
    {"input": "320a3120320a3320340a3520360a3720380a", "output": "5b313330372c20323936375d0a5b313531382c20333434365d0a"},
    {"input": "32202d3120322033202d342035202d36202d372038", "output": "5b313330372c202d323936375d0a5b2d313531382c20333434365d0a"},
    {"input": (b"200 " + b"1 "*40000 + b"-1 "*40000).hex(),
     "output": ((b"["+b", ".join([b"8000000"]*200)+b"]\n")*200).hex()}
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
