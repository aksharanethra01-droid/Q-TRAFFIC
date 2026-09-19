import json, time
from pathlib import Path
from scenarios.scenario_engine import ScenarioEngine
from scenarios.events import EVENT_TIMELINE

def main():
    engine=ScenarioEngine("Coimbatore")
    print("\n=== QUANTUM-ENHANCED ADAPTIVE URBAN TRAFFIC OPTIMIZATION ===")
    print("J1 -> J2 -> J3 -> J4 | rolling horizon 60s | p=2")
    for e in EVENT_TIMELINE:
        if e["type"]=="CROWD_SURGE" or e["type"]=="RECOVERY":
            continue
        result, preds = engine.step(e["type"], e["time"], e.get("junction"))
        q=result.qaoa
        print(f"\n[t={e['time']:>3}s] {e['type']}")
        print(" shock:", result.shock["affected"])
        print(" plans:", result.plans)
        print(" optimizer:", q["method"], q["status"], "objective=", q["objective_value"])
        if result.alert:
            print(" alert:", result.alert["english"])
            engine.metrics.add_alert(result.alert)
        if result.emergency:
            print(" emergency:", result.emergency["corridor_status"], result.emergency["clearance_status"])
        engine.metrics.add_qaoa_result(q)
        engine.metrics.add_scenario_result(result.__dict__ if hasattr(result,"__dict__") else result)
    print("\nOutputs written to outputs/")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
