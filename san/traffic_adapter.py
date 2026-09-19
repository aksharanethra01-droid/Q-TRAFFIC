import json


def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def build_traffic_state(dashboard_data, qubo_data):
    prediction = dashboard_data.get("prediction", {})

    congestion = qubo_data.get("congestion", {})

    shock = qubo_data.get("shock", {})
    shock_intensity = shock.get("intensity", {})

    junctions = {}

    for junction, values in prediction.items():

        capacity = max(float(values.get("capacity", 1)), 1)

        predicted = float(values.get("predicted", 0))

        junctions[junction] = {
            "density": float(values.get("density", 0)),
            "queue": float(values.get("queue", 0)),
            "speed": float(values.get("speed", 1)),
            "capacity": capacity,
            "predicted": predicted,

            "congestion": float(
                congestion.get(
                    junction,
                    min(predicted / capacity, 1.0)
                )
            ),

            "shock_intensity": float(
                shock_intensity.get(junction, 0)
            )
        }

    return {
        "location": dashboard_data.get("location"),
        "scenario": dashboard_data.get("scenario"),
        "junctions": junctions,
        "shock_source": shock.get("source"),
        "shock_propagation": shock.get("propagation", [])
    }


def load_and_adapt(dashboard_path, qubo_path):

    dashboard_data = load_json(dashboard_path)

    qubo_data = load_json(qubo_path)

    return build_traffic_state(
        dashboard_data,
        qubo_data
    )