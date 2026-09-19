import unittest
import networkx as nx
from san.emergency import EmergencyVehicle
from san.routing import candidate_routes,select_best_route
from san.corridor import build_green_corridor,junction_states,clearance_check
from san.recovery import recovery_plan
from san.emissions import estimate_fuel_and_co2
from san.dashboard_output import build_dashboard_output

class TestSanModule(unittest.TestCase):
    def setUp(self):
        self.g=nx.DiGraph()
        self.g.add_edge("J1","J2",distance=2,speed=20,congestion=.2,queue=2,closed=False)
        self.g.add_edge("J2","J5",distance=2,speed=20,congestion=.8,queue=12,closed=False)
        self.g.add_edge("J1","J4",distance=2,speed=20,congestion=.2,queue=2,closed=False)
        self.g.add_edge("J4","J5",distance=2,speed=20,congestion=.2,queue=2,closed=False)
    def test_emergency(self):
        self.assertEqual(EmergencyVehicle("AMB01","J1","J5").vehicle_type,"AMBULANCE")
    def test_routing(self):
        self.assertEqual(select_best_route(candidate_routes(self.g,"J1","J5",3))["route"],["J1","J4","J5"])
    def test_corridor(self):
        self.assertEqual(build_green_corridor(["J1","J4","J5"])["status"],"READY")
    def test_states(self):
        self.assertEqual(junction_states(["J1"])["J1"],"GREEN")
    def test_clearance(self):
        self.assertTrue(clearance_check({"queue":2,"downstream_clear":True})["clear"])
        self.assertFalse(clearance_check({"queue":20,"downstream_clear":True})["clear"])
    def test_recovery(self):
        self.assertEqual(recovery_plan(["J1"])["next_action"],"QAOA_REOPTIMIZATION")
    def test_emissions(self):
        self.assertGreater(estimate_fuel_and_co2(10,5,10)["fuel_litres"],0)
    def test_dashboard(self):
        a=EmergencyVehicle("AMB01","J1","J5")
        o=build_dashboard_output(a,["J1"],"ACTIVE",{"J1":"GREEN"},{"clear":True,"action":"PROCEED"},recovery_plan(["J1"]),estimate_fuel_and_co2(10,5,10))
        self.assertEqual(o["vehicle_type"],"AMBULANCE")

if __name__=="__main__": unittest.main()
