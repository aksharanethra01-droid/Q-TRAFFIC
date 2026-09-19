import asyncio
from pathlib import Path


VOICES = {
    "en": "en-IN-NeerjaNeural",
    "ta": "ta-IN-PallaviNeural",
}


async def _save_edge_tts(text, voice, output):
    import edge_tts

    communicator = edge_tts.Communicate(
        text=text,
        voice=voice,
    )

    await communicator.save(
        str(output)
    )


def generate_tts(
    text: str,
    language: str,
    output: str | Path,
):
    language = language.lower().strip()

    if language not in VOICES:
        language = "en"

    output = Path(output)

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    try:
        asyncio.run(
            _save_edge_tts(
                text=text,
                voice=VOICES[language],
                output=output,
            )
        )

        return {
            "status": "GENERATED",
            "language": language,
            "voice": VOICES[language],
            "path": str(output),
        }

    except Exception as exc:

        return {
            "status": "TTS UNAVAILABLE",
            "language": language,
            "voice": VOICES[language],
            "path": None,
            "error": str(exc),
        }


def generate_bilingual_tts(
    english_text: str,
    tamil_text: str,
    output_directory: str | Path,
    prefix: str = "traffic_alert",
):
    output_directory = Path(
        output_directory
    )

    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    english_output = (
        output_directory
        / f"{prefix}_english.mp3"
    )

    tamil_output = (
        output_directory
        / f"{prefix}_tamil.mp3"
    )

    english_result = generate_tts(
        english_text,
        "en",
        english_output,
    )

    tamil_result = generate_tts(
        tamil_text,
        "ta",
        tamil_output,
    )

    return {
        "english": english_result,
        "tamil": tamil_result,
    }