from pathlib import Path

from alerts.tts_alerts import generate_bilingual_tts


output = Path("outputs") / "voice_alerts"

result = generate_bilingual_tts(
    english_text=(
        "Vehicle TN38AB1234, Sedan, detected near J2 "
        "causing a traffic obstruction. "
        "Adaptive traffic optimization has been triggered."
    ),
    tamil_text=(
        "J2 அருகே TN38AB1234 Sedan வாகனம் "
        "போக்குவரத்துக்கு இடையூறு ஏற்படுத்துகிறது. "
        "தானியங்கி போக்குவரத்து மேம்படுத்தல் தொடங்கப்பட்டுள்ளது."
    ),
    output_directory=output,
    prefix="vehicle_obstruction",
)

print(result)