from metrics.fuel_model import estimate_fuel
from metrics.emissions import estimate_co2
from metrics.collector import MetricsCollector

def test_fuel_calculation():
    assert estimate_fuel(100,10,20)>0

def test_co2_calculation():
    assert estimate_co2(2)==4.62

def test_waiting_metrics(tmp_path):
    c=MetricsCollector(tmp_path)
    context={f"J{i}":{"waiting":10,"queue":5,"throughput":20,"vehicles":20,"capacity":50,
                         "emergency_delay":0,"fuel":1,"co2":2} for i in range(1,5)}
    row=c.record(0,"NORMAL",context,{"J1":"PLAN_1","J2":"PLAN_1","J3":"PLAN_1","J4":"PLAN_1"},.1,.01,0)
    assert row["total_waiting_time"]==40
    assert (tmp_path/"metrics.csv").exists()
