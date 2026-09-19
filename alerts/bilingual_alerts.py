from datetime import datetime, timezone

def generate_alert(event, location, vehicle_id="", vehicle_model="", impact="", ai_action=""):
    templates = {
        "VEHICLE_OBSTRUCTION": (
            f"Vehicle {vehicle_id}, {vehicle_model}, detected near {location} causing a lane obstruction. Traffic optimization has been triggered.",
            f"{location} அருகே {vehicle_id} {vehicle_model} வாகனம் பாதை தடையை ஏற்படுத்துகிறது. போக்குவரத்து சிக்னல் மேம்படுத்தல் தொடங்கப்பட்டுள்ளது."
        ),
        "ACCIDENT": (
            f"Accident detected near {location}. Traffic shock propagation and signal optimization have been triggered.",
            f"{location} அருகே விபத்து கண்டறியப்பட்டுள்ளது. போக்குவரத்து தாக்கப் பரவல் மற்றும் சிக்னல் மேம்படுத்தல் தொடங்கப்பட்டுள்ளது."
        ),
        "AMBULANCE": (
            f"Ambulance {vehicle_id} detected near {location}. Emergency green-corridor assessment has been triggered.",
            f"{location} அருகே ஆம்புலன்ஸ் {vehicle_id} கண்டறியப்பட்டுள்ளது. அவசர பசுமை வழித்தட மதிப்பீடு தொடங்கப்பட்டுள்ளது."
        ),
    }
    en, ta = templates.get(event, (f"{event} detected at {location}.", f"{location} பகுதியில் {event} கண்டறியப்பட்டது."))
    return {"event": event, "location": location, "vehicle_id": vehicle_id, "vehicle_model": vehicle_model,
            "impact": impact, "ai_action": ai_action, "english": en, "tamil": ta,
            "timestamp": datetime.now(timezone.utc).isoformat()}
