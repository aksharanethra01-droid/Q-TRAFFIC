"""
Q-TRAFFIC Congestion Prediction Engine

Uses the simulated traffic state to identify
current and predicted congestion.

This is a prototype prediction layer.
"""

def predict_congestion(traffic_state):
    """
    Analyze traffic conditions at each junction.

    Returns congestion information for every junction.
    """

    predictions = {}

    for junction, data in traffic_state.items():

        vehicles = data["vehicles"]
        queue = data["queue"]
        speed = data["speed"]
        capacity = data["capacity"]

        # Traffic density
        density = vehicles / capacity

        # Congestion score
        congestion_score = (
            (queue / capacity) * 0.5
            + ((30 - speed) / 30) * 0.3
            + density * 0.2
        )

        # Keep score between 0 and 1
        congestion_score = max(
            0,
            min(1, congestion_score)
        )

        # Classification
        if congestion_score >= 0.70:
            level = "CRITICAL"

        elif congestion_score >= 0.50:
            level = "HIGH"

        elif congestion_score >= 0.30:
            level = "MODERATE"

        else:
            level = "LOW"

        predictions[junction] = {
            "congestion_score": round(
                congestion_score,
                2
            ),
            "level": level,
            "density": round(density, 2),
            "queue": queue,
            "speed": speed
        }

    return predictions


def get_critical_junctions(predictions):
    """
    Return junctions predicted to have
    high or critical congestion.
    """

    critical = []

    for junction, result in predictions.items():

        if result["level"] in [
            "HIGH",
            "CRITICAL"
        ]:
            critical.append(junction)

    return critical


if __name__ == "__main__":

    # Temporary test traffic state
    traffic_state = {
        "J1": {
            "vehicles": 55,
            "queue": 28,
            "speed": 18,
            "capacity": 60
        },

        "J2": {
            "vehicles": 48,
            "queue": 22,
            "speed": 20,
            "capacity": 60
        },

        "J3": {
            "vehicles": 52,
            "queue": 39,
            "speed": 13,
            "capacity": 60
        },

        "J4": {
            "vehicles": 36,
            "queue": 14,
            "speed": 25,
            "capacity": 60
        }
    }

    predictions = predict_congestion(
        traffic_state
    )

    print("\nCONGESTION PREDICTION")
    print("=" * 50)

    for junction, result in predictions.items():

        print(
            f"{junction} | "
            f"Score: {result['congestion_score']} | "
            f"Level: {result['level']} | "
            f"Queue: {result['queue']} | "
            f"Speed: {result['speed']} km/h"
        )

    critical = get_critical_junctions(
        predictions
    )

    print("\nJUNCTIONS REQUIRING ATTENTION:")
    print(critical)