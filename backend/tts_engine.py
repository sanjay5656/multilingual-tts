import uuid
import torch
import soundfile as sf
from pathlib import Path

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"[TTS Engine] Using device: {DEVICE}")

OUTPUT_DIR = Path(__file__).parent.parent / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

# WHAT: Reference audio files for voice cloning
# WHY: Cloning from real audio gives much more natural output than built-in speakers
REFERENCES_DIR = Path(__file__).parent.parent / "references"
YOUNG_FEMALE_REF = str(REFERENCES_DIR / "young_female.wav")
YOUNG_MALE_REF   = str(REFERENCES_DIR / "young_male.wav")

# WHAT: Language to model mapping
# WHY: XTTS handles English/Hindi, MMS handles Dravidian languages
LANG_MODEL_MAP = {
    "en": "xtts",
    "hi": "xtts",
    "kn": "mms",
    "te": "mms",
    "ta": "mms",
}

# WHAT: 3-letter ISO codes for MMS
# WHY: Facebook MMS requires ISO 639-3 not ISO 639-1
MMS_LANG_CODES = {
    "kn": "kan",
    "te": "tel",
    "ta": "tam",
}

# WHAT: Voice type maps to reference file
# WHY: We only have two voices — young female and young male
# Both use cloning mode for maximum naturalness
VOICE_REFS = {
    "young_female": YOUNG_FEMALE_REF,
    "young_male":   YOUNG_MALE_REF,
}

xtts_model = None
mms_models = {}


def load_xtts():
    global xtts_model
    if xtts_model is not None:
        return
    print("[TTS Engine] Loading XTTS v2 model...")
    from TTS.api import TTS
    xtts_model = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(DEVICE)
    print("[TTS Engine] XTTS v2 loaded successfully")


def load_mms(lang_code):
    global mms_models
    if lang_code in mms_models:
        return
    from transformers import VitsModel, AutoTokenizer
    mms_code = MMS_LANG_CODES.get(lang_code, lang_code)
    model_name = f"facebook/mms-tts-{mms_code}"
    print(f"[TTS Engine] Loading MMS model: {model_name}")
    mms_models[lang_code] = {
        "model": VitsModel.from_pretrained(model_name).to(DEVICE),
        "tokenizer": AutoTokenizer.from_pretrained(model_name),
    }
    print(f"[TTS Engine] MMS {mms_code} loaded successfully")


def synthesize_xtts(text, language, voice_type="young_female", speaker_wav=None, speed=1.0):
    load_xtts()
    output_path = str(OUTPUT_DIR / f"{uuid.uuid4()}.wav")

    # WHAT: Pick reference file based on voice type
    # WHY: If user uploads their own voice, use that instead
    if speaker_wav:
        ref_audio = speaker_wav
        print(f"[TTS Engine] Using uploaded voice clone")
    else:
        ref_audio = VOICE_REFS.get(voice_type, YOUNG_FEMALE_REF)
        print(f"[TTS Engine] Using reference: {voice_type} → {ref_audio}")

    # WHAT: Clone mode — most natural output
    # WHY: Voice cloning from real audio sounds far better than built-in speakers
    xtts_model.tts_to_file(
        text=text,
        speaker_wav=ref_audio,
        language=language,
        file_path=output_path,
        speed=speed,
    )
    return output_path


def synthesize_mms(text, language, speed=1.0):
    load_mms(language)
    model_data = mms_models[language]
    model = model_data["model"]
    tokenizer = model_data["tokenizer"]

    inputs = tokenizer(text, return_tensors="pt").to(DEVICE)

    with torch.no_grad():
        output = model(**inputs).waveform

    waveform = output.squeeze().cpu().numpy()

    if speed != 1.0:
        try:
            import librosa
            waveform = librosa.effects.time_stretch(waveform, rate=float(speed))
        except Exception:
            pass

    output_path = str(OUTPUT_DIR / f"{uuid.uuid4()}.wav")
    sf.write(output_path, waveform, samplerate=16000)
    return output_path


def synthesize(text, language, voice_type="young_female", speaker_wav=None, speed=1.0):
    model_type = LANG_MODEL_MAP.get(language, "xtts")
    if model_type == "xtts":
        return synthesize_xtts(text, language, voice_type, speaker_wav, speed)
    else:
        return synthesize_mms(text, language, speed)
