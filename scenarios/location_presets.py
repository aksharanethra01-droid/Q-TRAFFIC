from copy import deepcopy
from config import LOCATIONS

def get_location(name: str):
    if name not in LOCATIONS:
        raise ValueError(f"Unknown location preset: {name}")
    return deepcopy(LOCATIONS[name])

def list_locations():
    return list(LOCATIONS)
