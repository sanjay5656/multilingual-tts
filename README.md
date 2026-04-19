# Multilingual Text-to-Speech System

A fully offline, open-source Text-to-Speech (TTS) web application that converts written text into natural, human-sounding speech across 5 Indian languages. Built with Python, FastAPI, and modern open-source AI models.

---

## Features

- Natural speech synthesis in English, Hindi, Kannada, Telugu, and Tamil
- Two natural voice types: Young Female and Young Male
- Voice cloning — upload a 3–5 second audio sample to speak in any voice
- Speaking speed control from 0.5x (slow) to 2.0x (fast)
- Download generated audio as WAV or MP3
- Clean, modern web UI accessible from any browser
- Fully offline after initial model download — no internet required at runtime
- GPU accelerated with NVIDIA CUDA support

---

## Models Used

| Model | Languages | Why Chosen |
|---|---|---|
| Coqui XTTS v2 | English, Hindi | Best open-source multilingual TTS, supports voice cloning, highly natural output |
| Facebook MMS (Massively Multilingual Speech) | Kannada, Telugu, Tamil | Only high-quality open-source model supporting Dravidian languages |

### Why Two Models?

XTTS v2 supports 17 languages but does not include Kannada, Telugu, or Tamil. Facebook MMS supports 1000+ languages including all Indian regional languages. By combining both models, we get the best possible quality for each language — XTTS for languages it handles well, MMS for regional Indian languages.

---

## Project Structure

```
multilingual-tts/
├── backend/
│   ├── main.py           # FastAPI server — handles HTTP requests
│   ├── tts_engine.py     # TTS model logic — loads and runs models
│   └── utils.py          # Helper functions — validation, conversion
├── frontend/
│   └── index.html        # Complete web UI — single file
├── references/           # Voice reference audio files (generated on first run)
├── outputs/              # Generated audio files (created at runtime)
├── requirements.txt      # Python dependencies
└── README.md
```

---

## System Requirements

| Component | Minimum | Recommended |
|---|---|---|
| Python | 3.11 | 3.11 or 3.12 |
| RAM | 8 GB | 16 GB |
| GPU | None (CPU works) | NVIDIA 4GB+ VRAM |
| Disk Space | 10 GB | 15 GB |
| OS | Linux / Windows / macOS | Ubuntu 22.04+ |

---

## Setup Instructions

### Step 1 — Clone the repository

```bash
git clone https://github.com/sanjay5656/multilingual-tts.git
cd multilingual-tts
```

### Step 2 — Create virtual environment

```bash
python3 -m venv venv

# Linux / macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### Step 3 — Install PyTorch

**For GPU (NVIDIA CUDA 12.1):**
```bash
pip install torch==2.4.0 torchaudio==2.4.0 --index-url https://download.pytorch.org/whl/cu121
```

**For CPU only:**
```bash
pip install torch==2.4.0 torchaudio==2.4.0
```

### Step 4 — Install all dependencies

```bash
pip install -r requirements.txt
```

### Step 5 — Generate voice reference files (first time only)

This step downloads the XTTS v2 model (~1.8 GB) and generates two reference voice files used for natural voice cloning.

```bash
mkdir -p references
python -c "
from TTS.api import TTS
tts = TTS('tts_models/multilingual/multi-dataset/xtts_v2')
print('Generating young female reference...')
tts.tts_to_file(
    text='Hello, I am happy to help you today. The weather is wonderful.',
    speaker='Gitta Nikolina',
    language='en',
    file_path='references/young_female.wav'
)
print('Generating young male reference...')
tts.tts_to_file(
    text='Hello, I am happy to help you today. The weather is wonderful.',
    speaker='Royston Min',
    language='en',
    file_path='references/young_male.wav'
)
print('Done.')
"
```

### Step 6 — Run the server

```bash
cd backend
python main.py
```

You should see:
```
[TTS Engine] Using device: cuda
INFO: Uvicorn running on http://0.0.0.0:8000
```

### Step 7 — Open the UI

Open your browser and go to:
```
http://localhost:8000/ui
```

---

## How to Use

1. Type or paste text in any supported language
2. Select the correct language from the language buttons
3. Choose voice type — Young Female or Young Male (English and Hindi only)
4. Adjust speaking speed using the slider if needed
5. Optionally upload a 3–5 second voice sample for voice cloning
6. Click **Generate Speech**
7. Play the audio directly in the browser
8. Download as WAV or MP3 using the download buttons

---

## Language Support

| Language | Script | Model | Voice Selection |
|---|---|---|---|
| English | Latin | Coqui XTTS v2 | Young Female / Young Male |
| Hindi | Devanagari | Coqui XTTS v2 | Young Female / Young Male |
| Kannada | ಕನ್ನಡ | Facebook MMS | Single voice |
| Telugu | తెలుగు | Facebook MMS | Single voice |
| Tamil | தமிழ் | Facebook MMS | Single voice |

> Note: Kannada, Telugu, and Tamil use Facebook MMS which provides a single high-quality voice per language. Voice type selection applies to English and Hindi only.

---

## API Reference

### POST /synthesize

Generate speech from text.

**Parameters (form-data):**

| Field | Type | Required | Description |
|---|---|---|---|
| text | string | Yes | Text to synthesize (max 1000 chars) |
| language | string | Yes | en / hi / kn / te / ta |
| voice_type | string | No | young_female / young_male (default: young_female) |
| speed | float | No | 0.5 to 2.0 (default: 1.0) |
| speaker_wav | file | No | Audio file for voice cloning |

**Example:**
```bash
curl -X POST http://localhost:8000/synthesize \
  -F "text=Hello world" \
  -F "language=en" \
  -F "voice_type=young_male" \
  -F "speed=1.0"
```

**Response:**
```json
{
  "status": "success",
  "audio_url": "/outputs/abc123.wav",
  "language": "en",
  "voice_type": "young_male"
}
```

### GET /health

Check server status.

```bash
curl http://localhost:8000/health
```

---

## Troubleshooting

**CUDA out of memory:**
> Stop any other processes using the GPU. The model needs ~2GB VRAM.

**Model download fails:**
> Check your internet connection during first run. After download, everything runs offline.

**Port 8000 already in use:**
```bash
# Change port in backend/main.py
uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
```

**Audio sounds robotic for regional languages:**
> This is a known limitation of the MMS model for Dravidian languages. MMS is currently the best available open-source option for offline Kannada/Telugu/Tamil synthesis.

---

## Technical Decisions

### Why FastAPI?
Lightweight, fast, automatic API documentation, easy file upload handling.

### Why not Gradio or Streamlit?
Custom HTML/CSS/JS gives full control over UI design and user experience without framework overhead.

### Why voice cloning instead of built-in speakers?
Voice cloning from reference audio produces significantly more natural output than XTTS built-in speaker embeddings.

### Why is MMS voice quality lower than XTTS?
Facebook MMS was trained primarily for speech recognition (STT), not synthesis (TTS). The TTS capability is available but limited compared to dedicated TTS models. No better open-source offline alternative exists for Kannada/Telugu/Tamil currently.

---

## Built With

- [Coqui TTS](https://github.com/coqui-ai/TTS) — XTTS v2 model
- [Facebook MMS](https://huggingface.co/facebook/mms-tts) — Massively Multilingual Speech
- [FastAPI](https://fastapi.tiangolo.com/) — Backend framework
- [PyTorch](https://pytorch.org/) — Deep learning runtime
- [HuggingFace Transformers](https://huggingface.co/transformers) — MMS model loading

---

## Author

Sanjay S
GitHub: [github.com/sanjay5656](https://github.com/sanjay5656)