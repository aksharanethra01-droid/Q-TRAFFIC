def estimate_fuel_and_co2(vehicle_count,idle_time_min,travel_time_min,
                          idle_fuel_rate=0.02,travel_fuel_rate=0.08,co2_per_litre=2.31):
    idle=max(vehicle_count,0)*max(idle_time_min,0)*idle_fuel_rate
    travel=max(vehicle_count,0)*max(travel_time_min,0)*travel_fuel_rate/60
    fuel=idle+travel
    return {"fuel_litres":round(fuel,3),"co2_kg":round(fuel*co2_per_litre,3),
            "assumptions":{"idle_fuel_rate_l_per_vehicle_min":idle_fuel_rate,
                           "travel_fuel_rate_l_per_vehicle_hour":travel_fuel_rate,
                           "co2_kg_per_litre":co2_per_litre}}
