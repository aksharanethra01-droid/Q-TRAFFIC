from pydantic import BaseModel
from typing import Optional, List, Dict, Any


# ============================================================
# SCENARIO REQUEST
# ============================================================

class ScenarioRequest(BaseModel):
    location: str
    scenario: str


# ============================================================
# TRAFFIC PREDICTION REQUEST
# ============================================================

class TrafficPredictionRequest(BaseModel):
    traffic_state: Dict[str, Any]


# ============================================================
# EMERGENCY ROUTE REQUEST
# ============================================================

class EmergencyRouteRequest(BaseModel):
    vehicle: str
    start: str
    destination: str
    priority: str = "HIGH"


# ============================================================
# SIGNAL OPTIMIZATION REQUEST
# ============================================================

class SignalOptimizationRequest(BaseModel):
    traffic_state: Dict[str, Any]
    emergency_junctions: List[str] = []


# ============================================================
# API RESPONSE
# ============================================================

class APIResponse(BaseModel):
    status: str
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None