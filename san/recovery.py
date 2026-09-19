def recovery_plan(route):
    return {
        "status":"READY","emergency_mode":"OFF","priority_removed":True,
        "route":list(route or []),"next_action":"QAOA_REOPTIMIZATION"
    }
