from pydantic import BaseModel


# =========================================================
# SCENARIO REQUEST
# =========================================================

class ScenarioRequest(BaseModel):
    location: str = "Coimbatore"
    scenario: str = "Normal Traffic"


# =========================================================
# TRAFFIC PREDICTION REQUEST
# =========================================================

class PredictionRequest(BaseModel):
    location: str = "Coimbatore"
    scenario: str = "Normal Traffic"


# =========================================================
# EMERGENCY ROUTE REQUEST
# =========================================================

class EmergencyRouteRequest(BaseModel):
    vehicle: str
    start: str
    destination: str
    priority: str = "HIGH"