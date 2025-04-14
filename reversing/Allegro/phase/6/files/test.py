#!/usr/bin/env python3
"""Sample testcases
Use this script to ensure that your improved program is at least not completely broken.
"""
import subprocess

PROG_NAME = './prog-6'
TESTCASE = [
    {"input": "3120312031", "output": "33333535343433320a"},
    {"input": "313233342033313420313539", "output": "343738383134383538323734373834313135310a"},
    {"input": "31323334353637382033313420313539", "output": "393833303036333339303032343831383733380a"},
    {"input": "3132333435363738392033313420313539", "output": "31383330323039383034313031333439393439300a"},
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
