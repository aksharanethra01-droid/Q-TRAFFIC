from emergency.route import find_emergency_route
from emergency.green_corridor import GreenCorridorController

def test_route_correct():
    assert find_emergency_route()=="J1 J2 J3 J4".split()

def test_clearance_logic():
    c=GreenCorridorController(["J1","J2","J3","J4"])
    traffic={j:{"queue":5,"capacity":50,"occupancy":.2} for j in ["J1","J2","J3","J4"]}
    d=c.evaluate("J1",traffic)
    assert d.corridor_status=="ACTIVE"
    assert set(d.active_signals)=={"J1","J2","J3","J4"}

def test_blocked_corridor():
    c=GreenCorridorController(["J1","J2","J3","J4"])
    traffic={j:{"queue":5,"capacity":50,"occupancy":.2} for j in ["J1","J2","J3","J4"]}
    traffic["J3"]["queue"]=30
    d=c.evaluate("J1",traffic)
    assert d.corridor_status=="HOLD"
