JUNCTIONS = ["J1", "J2", "J3", "J4", "J5"]

# Simple network used by the shock-propagation prototype.
# Each pair means traffic pressure can propagate from the first junction to the second.
NETWORK = {
    "J1": ["J2"],
    "J2": ["J1", "J3"],
    "J3": ["J2", "J4"],
    "J4": ["J3", "J5"],
    "J5": ["J4"],
}

DEFAULT_CAPACITY_REDUCTION = {
    "LOW": 0.25,
    "MEDIUM": 0.50,
    "HIGH": 0.75,
}

PREDICTION_HORIZONS = [1, 3, 5]
