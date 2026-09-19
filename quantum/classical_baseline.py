import itertools, time
from config import JUNCTIONS, PLAN_ORDER, SIGNAL_PLANS

def _bits_for_plans(plans):
    bits = []
    for j in JUNCTIONS:
        p = plans[j].replace("PLAN_", "P")
        bits.extend([1 if p == f"P{k}" else 0 for k in range(1,4)])
    return bits

def fixed_time_controller():
    return {j: "PLAN_2" for j in JUNCTIONS}

def rule_based_controller(context):
    out = {}
    for j in JUNCTIONS:
        s = context[j]
        ratio = s["queue"] / max(s["capacity"], 1)
        out[j] = "PLAN_3" if ratio >= 0.8 else ("PLAN_2" if ratio >= 0.45 else "PLAN_1")
    return out

def exact_classical_qubo(model):
    start = time.perf_counter()
    best = None
    for combo in itertools.product(PLAN_ORDER, repeat=4):
        plans = dict(zip(JUNCTIONS, combo))
        bits = _bits_for_plans(plans)
        obj = model.evaluate(bits)
        if best is None or obj < best[0]:
            best = (obj, plans, bits)
    return {
        "method": "EXACT_CLASSICAL_QUBO", "selected_plan": best[1],
        "objective": float(best[0]), "execution_time": time.perf_counter()-start,
        "waiting_time": None,
    }

def summarize_metrics(context, plans):
    # Same physical objective inputs used by the optimization context.
    waiting = sum(float(s["waiting"]) for s in context.values())
    queue = sum(float(s["queue"]) for s in context.values())
    throughput = sum(float(s["throughput"]) for s in context.values())
    emergency = sum(float(s.get("emergency_delay", 0)) for s in context.values())
    fuel = sum(float(s.get("fuel", 0)) for s in context.values())
    co2 = sum(float(s.get("co2", 0)) for s in context.values())
    return {"waiting": waiting, "queue": queue, "throughput": throughput,
            "emergency_delay": emergency, "fuel": fuel, "co2": co2}
