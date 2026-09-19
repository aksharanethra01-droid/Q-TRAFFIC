from typing import Dict, Tuple
from config import JUNCTIONS, PLAN_ORDER

def normalize_bitstring(bitstring: str, n: int = 12) -> str:
    s = "".join(c for c in bitstring if c in "01")
    if len(s) != n:
        raise ValueError(f"Expected {n} bits, got {len(s)}")
    return s

def decode_bitstring(bitstring: str) -> Tuple[Dict[str, str], bool]:
    s = normalize_bitstring(bitstring)
    plans = {}
    valid = True
    for i, j in enumerate(JUNCTIONS):
        block = s[i*3:(i+1)*3]
        if block.count("1") != 1:
            valid = False
            plans[j] = None
        else:
            plans[j] = PLAN_ORDER[block.index("1")]
    return plans, valid

def repair_bitstring(bitstring: str, cost_evaluator=None) -> tuple[str, Dict[str, str], bool]:
    s = normalize_bitstring(bitstring)
    plans, valid = decode_bitstring(s)
    if valid:
        return s, plans, False
    repaired = []
    for i in range(4):
        block = s[i*3:(i+1)*3]
        if "1" in block:
            # If multiple ones, retain the first unless a supplied objective can choose better.
            candidates = [k for k, b in enumerate(block) if b == "1"]
            if cost_evaluator:
                k = min(candidates, key=lambda c: cost_evaluator(i, c))
            else:
                k = candidates[0]
        else:
            candidates = range(3)
            k = min(candidates, key=lambda c: cost_evaluator(i, c) if cost_evaluator else c)
        repaired.extend("1" if k == c else "0" for c in range(3))
    rs = "".join(repaired)
    rp, _ = decode_bitstring(rs)
    return rs, rp, True
