#!/usr/bin/env python3
import subprocess

"""Sample testcases
Use this script to ensure that your improved program is at least not completely broken.
"""

def run_test(path: str, testcase: dict[str, str]) -> bool:
    p = subprocess.Popen([path],
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    try:
        stdout, _ = p.communicate(bytes.fromhex(testcase['input']), timeout=3)
    except subprocess.TimeoutExpired:
        print("[-] Timeout")
        return False
        
    assert stdout.hex() == testcase['output'], \
        f"Test failed: \n" \
        f"  Input: {bytes.fromhex(testcase['input'])}\n" \
        f"  Expected: {bytes.fromhex(testcase['output'])}" \
        f"  Output: {stdout}"

    return True

if __name__ == '__main__':
    testcase = [
        {"input": "313120312031", "output": "30303030303034380a"},
        {"input": "63383463646120313330642035", "output": "30303030343239380a"},
        {"input": "666238303634646434663530303763612065376337203230", "output": "30303031336438380a"},
        {"input": "303162663265326236626264366333632065393734203139", "output": "30303031646237660a"},
    ]

    ok = 0
    for i, test in enumerate(testcase):
        print(f"[+] Running test {i+1}/{len(testcase)}")
        if run_test('./ans-3', test):
            ok += 1

    print(f"[+] All tests passed ({ok}/{len(testcase)} are correct)")
