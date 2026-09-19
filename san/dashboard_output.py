def build_dashboard_output(vehicle,selected_route,corridor_status,junctions,
                           clearance,recovery,fuel_co2,candidate_routes=None):
    return {
        "vehicle":vehicle.vehicle_id,"vehicle_type":vehicle.vehicle_type,
        "start":vehicle.start,"destination":vehicle.destination,"priority":vehicle.priority,
        "candidate_routes":candidate_routes or [],"selected_route":selected_route or [],
        "corridor_status":corridor_status,"junctions":junctions,
        "clearance":clearance,"recovery":recovery,"fuel_co2_estimate":fuel_co2
    }
