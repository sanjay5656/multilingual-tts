import os
import uuid
from pathlib import Path
from pydub import AudioSegment

OUTPUT_DIR = Path(__file__).parent.parent / "outputs"


def generate_unique_filename(extension="wav"):
    return str(OUTPUT_DIR / f"{uuid.uuid4()}.{extension}")


def convert_wav_to_mp3(wav_path):
    mp3_path = wav_path.replace(".wav", ".mp3")
    audio = AudioSegment.from_wav(wav_path)
    audio.export(mp3_path, format="mp3")
    return mp3_path


def validate_text(text):
    if not text or not text.strip():
        return False, "Text cannot be empty"
    if len(text) > 1000:
        return False, "Text too long. Maximum 1000 characters"
    return True, "Valid"


def validate_language(language):
    supported = ["en", "hi", "kn", "te", "ta"]
    if language not in supported:
        return False, f"Language '{language}' not supported"
    return True, "Valid"
